"""
Jenkins Documentation Scraper

Scrapes Jenkins Pipeline documentation from jenkins.io and generates jenkins_data.json
"""

import json
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup

# Configuration
JENKINS_BASE_URL = 'https://www.jenkins.io'
JENKINS_REFERENCE_URL = f'{JENKINS_BASE_URL}/doc/pipeline/steps/'
OUTPUT_FILE = '../jenkins_data.json'
OUTPUT_FILE_FORMATTED = '../jenkins_data_formatted.json'  # Optional formatted version
REQUEST_DELAY = 0.1  # Delay between requests to avoid overwhelming the server
SAVE_FORMATTED_VERSION = False  # Set to True if you want both minified and formatted versions

# Environment variables (static data)
ENVIRONMENT_VARIABLES = [
    {"name": "BUILD_NUMBER", "description": "The current build number"},
    {"name": "BUILD_ID", "description": "The current build ID"},
    {"name": "BUILD_DISPLAY_NAME", "description": "Display name of the current build"},
    {"name": "JOB_NAME", "description": "Name of the project of this build"},
    {"name": "BUILD_TAG", "description": "String of jenkins-${JOB_NAME}-${BUILD_NUMBER}"},
    {"name": "EXECUTOR_NUMBER", "description": "The unique number that identifies the current executor"},
    {"name": "NODE_NAME", "description": "Name of the node the current build is running on"},
    {"name": "NODE_LABELS", "description": "Whitespace-separated list of labels assigned to the node"},
    {"name": "WORKSPACE", "description": "The absolute path of the workspace"},
    {"name": "JENKINS_HOME", "description": "The absolute path on the master node for Jenkins to store data"},
    {"name": "JENKINS_URL", "description": "Full URL of Jenkins"},
    {"name": "BUILD_URL", "description": "Full URL of this build"},
    {"name": "JOB_URL", "description": "Full URL of this job"},
]


class JenkinsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.jenkins_data = {
            'date': datetime.now().isoformat(),
            'plugins': [],
            'instructions': [],
            'sections': [],
            'directives': [],
            'environmentVariables': ENVIRONMENT_VARIABLES
        }

    def scrape_all(self):
        """Main scraping function"""
        print("Starting Jenkins documentation scraper...")

        # Scrape sections and directives first
        print("\nScraping sections...")
        self.scrape_sections()

        print("\nScraping directives...")
        self.scrape_directives()

        # Scrape plugins and their steps
        print("\nFetching plugins list...")
        self.scrape_plugins()

        print("\nScraping plugin documentation...")
        self.scrape_plugin_steps()

        # Save to file
        self.save_data()

        print(f"\n✓ Scraping complete!")
        print(f"  - {len(self.jenkins_data['plugins'])} plugins")
        print(f"  - {len(self.jenkins_data['instructions'])} instructions")
        print(f"  - {len(self.jenkins_data['sections'])} sections")
        print(f"  - {len(self.jenkins_data['directives'])} directives")

    def scrape_plugins(self):
        """Scrape the list of plugins from the main page"""
        try:
            response = self.session.get(JENKINS_REFERENCE_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')

            # Find plugin list
            plugin_list = soup.select('div.container div.col-lg-9 div > ul > li')

            for plugin_elem in plugin_list:
                link = plugin_elem.find('a')
                if link:
                    name = link.get_text(strip=True)
                    href = link.get('href', '')
                    url = f"{JENKINS_BASE_URL}{href}" if href else ""
                    plugin_id = url.rstrip('/').split('/')[-1].lower() if url else 'unknown'

                    self.jenkins_data['plugins'].append({
                        'name': name,
                        'url': url,
                        'id': plugin_id
                    })

            print(f"  Found {len(self.jenkins_data['plugins'])} plugins")

        except Exception as e:
            print(f"  Error fetching plugins list: {e}")

    def scrape_plugin_steps(self):
        """Scrape documentation for each plugin"""
        for i, plugin in enumerate(self.jenkins_data['plugins'], 1):
            try:
                print(f"  [{i}/{len(self.jenkins_data['plugins'])}] {plugin['name']}", end=' ')

                response = self.session.get(plugin['url'])
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'lxml')

                # Find all step documentation sections
                steps = soup.select('.sect2')
                step_count = 0

                for step_elem in steps:
                    step = self.parse_step(step_elem, plugin)
                    if step:
                        self.jenkins_data['instructions'].append(step)
                        step_count += 1

                print(f"→ {step_count} instructions")

                # Delay to avoid overwhelming the server
                time.sleep(REQUEST_DELAY)

            except Exception as e:
                print(f"→ Error: {e}")

    def parse_step(self, step_elem, plugin) -> Dict[str, Any]:
        """Parse a single step from documentation"""
        try:
            # Get command name
            command_elem = step_elem.select_one('h3 > code')
            if not command_elem:
                return None

            command = command_elem.get_text(strip=True)

            # Get full name
            name_elem = step_elem.select_one('h3')
            name = name_elem.get_text(strip=True) if name_elem else command

            # Get URL
            anchor = step_elem.select_one('h3 > a.anchor')
            url = f"{plugin['url']}{anchor.get('href')}" if anchor and anchor.get('href') else plugin['url']

            # Get description
            desc_elem = step_elem.select_one('div')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Parse parameters
            parameters = []
            param_elems = step_elem.select('ul > li')

            for param_elem in param_elems:
                param = self.parse_parameter(param_elem)
                if param:
                    parameters.append(param)

            return {
                'command': command,
                'name': name,
                'instructionType': 'Step',
                'description': description,
                'parameters': parameters,
                'plugin': plugin['id'],
                'url': url
            }

        except Exception as e:
            print(f"Error parsing step: {e}")
            return None

    def parse_parameter(self, param_elem) -> Dict[str, Any]:
        """Parse a parameter from step documentation"""
        try:
            # Get parameter name
            name_elem = param_elem.select_one('code')
            if not name_elem:
                return None

            name = name_elem.get_text(strip=True)

            # Get description
            desc_elem = param_elem.select_one('div')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Check if optional
            text_content = param_elem.get_text().lower()
            is_optional = 'optional' in text_content

            # Parse type and values
            param_type = 'String'
            values = []

            # Look for type or values
            type_elem = param_elem.select_one('ul > li > b, ul > b')
            if type_elem:
                type_text = type_elem.get_text(strip=True).lower()

                if type_text == 'type:':
                    type_code = param_elem.select_one('ul > li > code')
                    if type_code:
                        param_type = type_code.get_text(strip=True)

                elif type_text == 'values:':
                    param_type = 'Enum'
                    value_codes = param_elem.select('ul > li > code')
                    values = [v.get_text(strip=True) for v in value_codes]

            return {
                'name': name,
                'type': param_type,
                'values': values,
                'instructionType': 'Parameter',
                'description': description,
                'isOptional': is_optional
            }

        except Exception as e:
            print(f"Error parsing parameter: {e}")
            return None

    def scrape_sections(self):
        """Scrape Pipeline sections documentation"""
        # Static data for sections (as they're well-defined in Jenkins)
        sections = [
            {
                'name': 'agent',
                'instructionType': 'Section',
                'description': 'The agent section specifies where the entire Pipeline will execute',
                'allowed': 'Top-level of pipeline block, inside stage',
                'innerInstructions': ['any', 'none', 'label', 'docker', 'dockerfile'],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#agent',
                'isOptional': False
            },
            {
                'name': 'post',
                'instructionType': 'Section',
                'description': 'The post section defines actions to be run at the end of the Pipeline',
                'allowed': 'Top-level of pipeline block, inside stage',
                'innerInstructions': ['always', 'changed', 'fixed', 'regression', 'aborted', 'failure', 'success', 'unstable', 'unsuccessful', 'cleanup'],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#post',
                'isOptional': True
            },
            {
                'name': 'stages',
                'instructionType': 'Section',
                'description': 'Contains a sequence of one or more stage directives',
                'allowed': 'Top-level of pipeline block',
                'innerInstructions': [],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#stages',
                'isOptional': False
            },
            {
                'name': 'stage',
                'instructionType': 'Section',
                'description': 'A section defining a part of the Pipeline',
                'allowed': 'Inside stages section',
                'innerInstructions': [],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#stage',
                'isOptional': False
            },
            {
                'name': 'steps',
                'instructionType': 'Section',
                'description': 'Contains a sequence of one or more step directives',
                'allowed': 'Inside each stage block',
                'innerInstructions': [],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#steps',
                'isOptional': False
            }
        ]

        self.jenkins_data['sections'] = sections
        print(f"  Added {len(sections)} sections")

    def scrape_directives(self):
        """Scrape Pipeline directives documentation"""
        # Static data for directives
        directives = [
            {
                'name': 'environment',
                'instructionType': 'Directive',
                'description': 'Specifies environment variables to be set for all steps',
                'allowed': 'Top-level of pipeline block, inside stage',
                'innerInstructions': [],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#environment',
                'isOptional': True
            },
            {
                'name': 'options',
                'instructionType': 'Directive',
                'description': 'Allows configuring Pipeline-specific options',
                'allowed': 'Top-level of pipeline block, inside stage',
                'innerInstructions': ['buildDiscarder', 'checkoutToSubdirectory', 'disableConcurrentBuilds', 'disableResume', 'newContainerPerStage', 'overrideIndexTriggers', 'preserveStashes', 'quietPeriod', 'retry', 'skipDefaultCheckout', 'skipStagesAfterUnstable', 'timeout', 'timestamps', 'parallelsAlwaysFailFast'],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#options',
                'isOptional': True
            },
            {
                'name': 'parameters',
                'instructionType': 'Directive',
                'description': 'Provides a list of parameters for the build',
                'allowed': 'Top-level of pipeline block',
                'innerInstructions': ['string', 'text', 'booleanParam', 'choice', 'password'],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#parameters',
                'isOptional': True
            },
            {
                'name': 'triggers',
                'instructionType': 'Directive',
                'description': 'Defines automated ways in which the Pipeline should be re-triggered',
                'allowed': 'Top-level of pipeline block',
                'innerInstructions': ['cron', 'pollSCM', 'upstream'],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#triggers',
                'isOptional': True
            },
            {
                'name': 'tools',
                'instructionType': 'Directive',
                'description': 'Defines tools to auto-install and put on the PATH',
                'allowed': 'Top-level of pipeline block, inside stage',
                'innerInstructions': ['maven', 'jdk', 'gradle'],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#tools',
                'isOptional': True
            },
            {
                'name': 'input',
                'instructionType': 'Directive',
                'description': 'Allows prompting for input during Pipeline execution',
                'allowed': 'Inside stage',
                'innerInstructions': [],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#input',
                'isOptional': True
            },
            {
                'name': 'when',
                'instructionType': 'Directive',
                'description': 'Allows the Pipeline to determine whether the stage should be executed',
                'allowed': 'Inside stage',
                'innerInstructions': ['branch', 'buildingTag', 'changelog', 'changeset', 'changeRequest', 'environment', 'equals', 'expression', 'tag', 'not', 'allOf', 'anyOf', 'triggeredBy'],
                'url': 'https://www.jenkins.io/doc/book/pipeline/syntax/#when',
                'isOptional': True
            }
        ]

        self.jenkins_data['directives'] = directives
        print(f"  Added {len(directives)} directives")

    def save_data(self):
        """Save scraped data to JSON file"""
        # Sort instructions alphabetically
        self.jenkins_data['instructions'].sort(key=lambda x: x['command'])

        # Save minified JSON (no indentation, no spaces after separators)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.jenkins_data, f, separators=(',', ':'), ensure_ascii=False)

        # Calculate file size for reporting
        file_size = os.path.getsize(OUTPUT_FILE)
        size_mb = file_size / (1024 * 1024)

        print(f"\n✓ Data saved to {OUTPUT_FILE}")
        print(f"  File size: {size_mb:.1f} MB (minified)")

        # Optionally save formatted version for development/debugging
        if SAVE_FORMATTED_VERSION:
            with open(OUTPUT_FILE_FORMATTED, 'w', encoding='utf-8') as f:
                json.dump(self.jenkins_data, f, indent=2, ensure_ascii=False)

            formatted_size = os.path.getsize(OUTPUT_FILE_FORMATTED)
            formatted_mb = formatted_size / (1024 * 1024)

            print(f"  Formatted version saved to {OUTPUT_FILE_FORMATTED}")
            print(f"  Formatted size: {formatted_mb:.1f} MB")
            print(f"  Size reduction: {((formatted_size - file_size) / formatted_size * 100):.1f}%")


def main():
    scraper = JenkinsScraper()
    scraper.scrape_all()


if __name__ == '__main__':
    main()
