# Card statements

Works out a credit card holder's monthly statement: what is still outstanding, how many
days late the payment is, the late fee, one month of interest, and the total due.

## Run it

```bash
uv run python main.py     # statements for the sample accounts
uv run python -m pytest -q
```

Needs [uv](https://docs.astral.sh/uv/), which brings Python and the test tools on the first run.
The app itself uses only the standard library.

## Layout

```text
main.py                 Prints statements for the sample accounts.
billing/models.py       Account and Statement.
billing/statement.py    Builds a statement for an account on a given day.
billing/fees.py         The late fee: rate, minimum and maximum.
billing/interest.py     One month of interest.
billing/sample.py       Dummy accounts.
tests/                  pytest tests.
```

Money is `Decimal`, rounded to the cent. The sample data is made up.

## Workshop

The prompts for this exercise are in [PROMPTS.md](../../PROMPTS.md) at the repo root. Open
it in your browser or an editor, not in Claude Code.
