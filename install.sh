#!/bin/bash
echo ""
echo "=================================="
echo "  Agent Cost Proxy v0.2 - Setup"
echo "=================================="
echo ""
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --quiet
echo ""
echo "  Done. Run:"
echo ""
echo "    source .venv/bin/activate"
echo "    python3 proxy.py"
echo ""
echo "  Then in another terminal:"
echo ""
echo "    curl -s http://localhost:8080/fetch \\"
echo "      -H 'content-type: application/json' \\"
echo "      -d '{\"url\": \"https://finance.yahoo.com/quote/AAPL/\"}' \\"
echo "      | python3 -m json.tool"
echo ""
