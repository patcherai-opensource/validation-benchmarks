# PhpSpreadsheet sample application constants

# Supported currency codes for the NumberFormat Wizard
VALID_CURRENCIES = [
    'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'INR', 'BRL', 'CAD', 'AUD', 'CHF',
    'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RUB', 'TRY', 'ZAR', 'MXN',
    'SGD', 'HKD', 'NZD', 'KRW', 'THB', 'MYR', 'PHP', 'IDR', 'VND', 'AED',
    'SAR', 'ILS', 'EGP', 'NGN', 'KES', 'ARS', 'CLP', 'COP', 'PEN', 'TWD',
]

# Currency symbol mapping
CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '\u20ac',
    'GBP': '\u00a3',
    'JPY': '\u00a5',
    'CNY': '\u00a5',
    'INR': '\u20b9',
    'BRL': 'R$',
    'CAD': 'C$',
    'AUD': 'A$',
    'CHF': 'CHF',
    'SEK': 'kr',
    'NOK': 'kr',
    'DKK': 'kr',
    'PLN': 'z\u0142',
    'CZK': 'K\u010d',
    'HUF': 'Ft',
    'RUB': '\u20bd',
    'TRY': '\u20ba',
    'ZAR': 'R',
    'MXN': 'Mex$',
    'SGD': 'S$',
    'HKD': 'HK$',
    'NZD': 'NZ$',
    'KRW': '\u20a9',
    'THB': '\u0e3f',
    'MYR': 'RM',
    'PHP': '\u20b1',
    'IDR': 'Rp',
    'VND': '\u20ab',
    'AED': 'AED',
    'SAR': 'SAR',
    'ILS': '\u20aa',
    'EGP': 'EGP',
    'NGN': '\u20a6',
    'KES': 'KSh',
    'ARS': 'AR$',
    'CLP': 'CL$',
    'COP': 'COL$',
    'PEN': 'S/.',
    'TWD': 'NT$',
}

# Default formatting options
DEFAULT_DECIMALS = 2
DEFAULT_THOUSANDS = True
DEFAULT_POSITION = True  # True = before, False = after
DEFAULT_SPACING = False
