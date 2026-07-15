#!/bin/bash
#
# Quick Start Validation Script
#
# This script runs the complete Phase 3A validation flow:
# 1. Generates cache (one-time, ~3 min)
# 2. Runs deterministic validation (~25 min)
#
# Usage: ./run_validation.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================================"
echo "PHASE 3A DETERMINISTIC VALIDATION - QUICK START"
echo "================================================================================"
echo ""

# Check we're in the right directory
if [ ! -f "cache_validation_data.py" ]; then
    echo -e "${RED}❌ ERROR: cache_validation_data.py not found${NC}"
    echo "   Please run this script from the tradingagents directory"
    exit 1
fi

# Check for OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ ERROR: OPENAI_API_KEY not set${NC}"
    echo ""
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='sk-your-key-here'"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ OPENAI_API_KEY found${NC}"
echo ""

# Check if cache already exists
CACHE_FILE="validation_cache/cached_data_HDFCBANK.NS_2024-01-15.json"

if [ -f "$CACHE_FILE" ]; then
    echo -e "${YELLOW}⚠️  Cache file already exists: $CACHE_FILE${NC}"
    echo ""
    echo "Options:"
    echo "  1. Use existing cache (faster, recommended if recent)"
    echo "  2. Regenerate cache (slower, ensures fresh data)"
    echo "  3. Abort"
    echo ""
    read -p "Choose option (1/2/3): " choice
    
    case $choice in
        1)
            echo -e "${BLUE}→ Using existing cache${NC}"
            SKIP_CACHE=true
            ;;
        2)
            echo -e "${BLUE}→ Regenerating cache${NC}"
            rm -f "$CACHE_FILE"
            SKIP_CACHE=false
            ;;
        3)
            echo "Aborted by user"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Aborting.${NC}"
            exit 1
            ;;
    esac
else
    SKIP_CACHE=false
fi

echo ""

# Step 1: Generate cache (if needed)
if [ "$SKIP_CACHE" = false ]; then
    echo "================================================================================"
    echo "STEP 1: GENERATING VALIDATION CACHE"
    echo "================================================================================"
    echo ""
    echo "This will fetch and cache all external data."
    echo "Time: ~3 minutes"
    echo "Cost: ~$0.00 (data retrieval only)"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to abort..."
    echo ""
    
    if ./venv/bin/python cache_validation_data.py; then
        echo ""
        echo -e "${GREEN}✅ Cache generation complete${NC}"
    else
        echo ""
        echo -e "${RED}❌ Cache generation failed${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Using existing cache${NC}"
fi

echo ""
echo "Waiting 5 seconds before validation..."
sleep 5
echo ""

# Step 2: Run validation
echo "================================================================================"
echo "STEP 2: RUNNING DETERMINISTIC VALIDATION"
echo "================================================================================"
echo ""
echo "This will run baseline and optimized workflows with cached data."
echo "Time: ~25 minutes"
echo "Cost: ~$0.30"
echo ""
echo "The validation will:"
echo "  1. Load cached data (deterministic replay)"
echo "  2. Git stash Phase 3A changes"
echo "  3. Run BASELINE (pre-Phase-3A, 3 debate rounds)"
echo "  4. Git stash pop Phase 3A changes"
echo "  5. Run OPTIMIZED (Phase-3A, 2 debate rounds)"
echo "  6. Generate comparison report"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."
echo ""

# Set environment variables
export VALIDATION_CACHE_ONLY=true
export AUDIT_MODE=1
export USE_OPTIMIZED_ANALYSTS=1
export USE_OPTIMIZED_RISK=1

echo -e "${BLUE}Environment configured:${NC}"
echo "  VALIDATION_CACHE_ONLY=true"
echo "  AUDIT_MODE=1"
echo "  USE_OPTIMIZED_ANALYSTS=1"
echo "  USE_OPTIMIZED_RISK=1"
echo ""

# Run validation and capture output
LOGFILE="validation_$(date +%Y%m%d_%H%M%S).log"

echo -e "${BLUE}→ Running validation (logging to $LOGFILE)...${NC}"
echo ""

if ./venv/bin/python validate_git_based.py 2>&1 | tee "$LOGFILE"; then
    echo ""
    echo "================================================================================"
    echo "VALIDATION COMPLETE"
    echo "================================================================================"
    echo ""
    echo -e "${GREEN}✅ Validation completed successfully${NC}"
    echo ""
    echo "Log file: $LOGFILE"
    echo ""
    
    # Check for PASS in output
    if grep -q "STAGE 1 PASSED" "$LOGFILE"; then
        echo -e "${GREEN}✅✅✅ STAGE 1 PASSED ✅✅✅${NC}"
        echo ""
        echo "Phase 3A optimizations validated successfully!"
        echo "Proceed to Stage 2 (all 3 stocks)."
    elif grep -q "STAGE 1 FAILED" "$LOGFILE"; then
        echo -e "${RED}❌ STAGE 1 FAILED${NC}"
        echo ""
        echo "Review the log file for details: $LOGFILE"
    else
        echo -e "${YELLOW}⚠️  Validation completed but result unclear${NC}"
        echo "Review the log file: $LOGFILE"
    fi
else
    echo ""
    echo "================================================================================"
    echo "VALIDATION ERROR"
    echo "================================================================================"
    echo ""
    echo -e "${RED}❌ Validation failed with errors${NC}"
    echo ""
    echo "Log file: $LOGFILE"
    echo ""
    echo "Common issues:"
    echo "  - Cache file missing or corrupted"
    echo "  - Git state issues"
    echo "  - API rate limits"
    echo ""
    echo "See DETERMINISTIC_VALIDATION_GUIDE.md for troubleshooting"
    exit 1
fi

echo ""
echo "================================================================================"
echo "NEXT STEPS"
echo "================================================================================"
echo ""
echo "If PASSED:"
echo "  1. Review validation report in log file"
echo "  2. Proceed to Stage 2 (validate all 3 stocks)"
echo "  3. Generate deployment recommendation"
echo ""
echo "If FAILED:"
echo "  1. Analyze failure cause from log"
echo "  2. Adjust optimization parameters"
echo "  3. Re-run validation with same cache"
echo ""
echo "================================================================================"
