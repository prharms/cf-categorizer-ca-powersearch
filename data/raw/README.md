# Raw Data Directory

Place your cleaned PowerSearch CSV exports here.

## Files to include:
- Your downloaded PowerSearch CSV files
- Remove any footer/summary lines before processing

## Security Note:
This directory is excluded from Git to protect privacy.
Never commit real campaign finance data to public repositories.

## Example usage:
```bash
# Place your file here
data/raw/my_campaign_data.csv

# Then run the categorizer
python scripts/run_categorization.py data/raw/my_campaign_data.csv
```

## File Format:
Your CSV files should have these required columns:
- `Contributor Name`
- `Contributor Employer` 
- `Contributor Occupation`

Export these from the California Secretary of State PowerSearch portal:
https://powersearch.sos.ca.gov/advanced.php 