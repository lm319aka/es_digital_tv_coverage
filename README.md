# Spanish Digital Terrestrial Television (DTT) Coverage Checker

This Python script allows you to check Digital Terrestrial Television (DTT) coverage information for Spanish postal codes using the official Spanish government website: [https://television.digital.gob.es/](https://television.digital.gob.es/)

## Features

- Check DTT coverage for any valid Spanish postal code
- Batch process multiple postal codes with progress tracking
- Save results in JSONL format on txt file for easy processing
- Resume interrupted operations from the last processed postal code
- Option to reuse browser sessions for better performance

## Requirements

- Python 3.7+
- Google Chrome browser installed
- ChromeDriver (automatically installed by the script)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/lm319aka/es_digital_tv_coverage.git
   cd es_digital_tv_coverage
   ```

2. Create a virtual environment (venv) to manage libraries:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:

   ```bash
   .venv/bin/activate
   ```

4. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

### PD: Maybe you could have problems with undetectable_chromedriver because of incompatibility of libraries if a version that uses deprecated libraries is installed. If that is the case, you can try to clone the newer version of undetected_chromedriver from github and install it manually

## Usage

### Check a Single Postal Code

```python
from tdtc import coverage_tdt

# Get coverage for a single postal code
coverage_data, driver, wait = coverage_tdt("28001")
print(coverage_data)

# Remember to close the browser when done
driver.quit()
```

### Batch Process Multiple Postal Codes range

```python
from tdtc import get_all_coverage_data

# Process a range of postal codes (inclusive)
get_all_coverage_data(
    output_file="coverage_results.jsonl",
    start=28000,
    end=28999,
    progress_file="progress.txt"
)
```

### Command Line Interface

You can also run the script directly to check a single postal code:

```bash
python tdtc.py 08007
```

## Output Format

The script returns data in the following JSON format:

```json
{
  "Postal code": "28001",
  "Populations": [
    {
      "Population": "MADRID",
      "Data": [
        ["Multiple Digital 1", "Centro Emisor 1", "Canal 1"],
        ["Multiple Digital 2", "Centro Emisor 2", "Canal 2"]
      ]
    }
  ]
}
```

## Notes

- The script uses Selenium with undetected-chromedriver to avoid detection
- Cookies are saved to `tdtc_cookies.json` to maintain session state
- Progress is tracked in `progress.txt` to allow resuming interrupted operations
- The script includes delays to avoid overwhelming the target website

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE.txt) file for details.

## Disclaimer

This project is for educational and personal use only. Please respect the terms of service of the target website and use this script responsibly.
