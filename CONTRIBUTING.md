# Contributing

Contributions to Battery Charge Manager are accepted through GitHub pull requests.

## Contributor License Agreement

By submitting a contribution to this repository, you confirm that you have the legal right to provide it and agree to the following terms:

1. You retain copyright ownership of your contribution.
2. You grant Roman Zambail a perpetual, worldwide, non-exclusive, royalty-free, and irrevocable license to use, reproduce, modify, distribute, sublicense, and relicense your contribution.
3. The relicensing right expressly includes distribution of the contribution as part of Battery Charge Manager under the PolyForm Noncommercial License 1.0.0 and under separate commercial or proprietary licenses.
4. You confirm that the contribution does not knowingly contain material that you are not entitled to license under these terms.
5. The contribution is provided without warranty to the extent permitted by law.

Submitting a pull request constitutes acceptance of this Contributor License Agreement for the contribution in that pull request.

## Development requirements

- Keep changes focused and explain their purpose.
- Preserve safe switch-off behavior and the distinction between charger control and battery-protection electronics.
- Retain historical measurement records and revision filtering.
- Add or update tests for measurement and endpoint logic.
- Keep `manifest.json`, translations, README, and changelog synchronized with user-visible changes.
- Run Python compilation, JSON validation, JavaScript syntax checking, HACS validation, and hassfest.
