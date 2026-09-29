import json
import pytest
from twi_grapheme_fixer.cli import main


def test_cli_direct_text(capsys):
    ret = main(["aduane ne pono"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "àduané né pônô" in captured.out


def test_cli_reverse(capsys):
    ret = main(["-d", "reverse", "àduané né pônô"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "aduane ne pono" in captured.out


def test_cli_file_in_out(tmp_path):
    in_file = tmp_path / "in.txt"
    out_file = tmp_path / "out.txt"
    in_file.write_text("Kofi kɔɔ school no mu\n", encoding="utf-8")

    ret = main(["-i", str(in_file), "-o", str(out_file)])
    assert ret == 0
    content = out_file.read_text(encoding="utf-8")
    assert "Kôfi kɔɔ school nô mu" in content


def test_cli_report(capsys):
    ret = main(["--report", "Kofi kɔɔ school yesterday"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "--- Twi Grapheme Fixer Report ---" in captured.err
    assert "English exempted:" in captured.err


def test_cli_custom_exceptions(tmp_path, capsys):
    exc_file = tmp_path / "exceptions.json"
    exc_file.write_text(json.dumps({"testword": "téstwôrd"}), encoding="utf-8")

    ret = main(["--custom-exceptions", str(exc_file), "testword"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "téstwôrd" in captured.out
