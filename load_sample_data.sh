#!/bin/bash

# PeMost Backend - Sample Data Loader Script
# This script loads all sample data into the Docker container

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="pemost_backend"
COMPOSE_FILE="docker-compose-dev.yml"

# Default farm upload mode
FARM_MODE="skip"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --farm-mode)
            FARM_MODE="$2"
            shift 2
            ;;
        --clear-farms)
            CLEAR_FARMS="--clear"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --farm-mode MODE    Set farm upload mode: skip (default), update, or create"
            echo "  --clear-farms       Clear all existing farms before importing"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Load data with default settings (skip existing farms)"
            echo "  $0 --farm-mode update        # Update existing farms"
            echo "  $0 --clear-farms             # Clear all farms then import"
            echo "  $0 --farm-mode create        # Fail if duplicate farms exist"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Validate farm mode
if [[ ! "$FARM_MODE" =~ ^(skip|update|create)$ ]]; then
    echo -e "${RED}Error: Invalid farm mode '$FARM_MODE'. Must be: skip, update, or create${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PeMost Backend - Sample Data Loader${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Farm Upload Mode: ${YELLOW}$FARM_MODE${NC}"
if [ -n "$CLEAR_FARMS" ]; then
    echo -e "${YELLOW}Warning: All existing farms will be cleared!${NC}"
fi
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/8]${NC} Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker is running.${NC}\n"

# Check if docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}Error: $COMPOSE_FILE not found!${NC}"
    exit 1
fi

# Check if container is running
echo -e "${YELLOW}[2/8]${NC} Checking if $CONTAINER_NAME container is running..."
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}Error: Container $CONTAINER_NAME is not running.${NC}"
    echo -e "${YELLOW}Please start the containers first with: docker-compose -f $COMPOSE_FILE up -d${NC}"
    exit 1
fi
echo -e "${GREEN}Container is running.${NC}\n"

# Function to execute command in container
exec_command() {
    local step=$1
    local description=$2
    local command=$3

    echo -e "${YELLOW}[$step]${NC} $description"
    echo -e "${BLUE}Running:${NC} $command"

    if docker exec -it $CONTAINER_NAME bash -c "cd /pemostbackend && $command"; then
        echo -e "${GREEN}Success!${NC}\n"
        return 0
    else
        echo -e "${RED}Failed!${NC}\n"
        return 1
    fi
}

# Track failed commands
FAILED_COMMANDS=()

# Load Locations (Counties, Subcounties, Wards)
if ! exec_command "3/8" "Loading locations (Counties, Subcounties, Wards)..." \
    "python manage.py load_locations sample_data/locations.csv"; then
    FAILED_COMMANDS+=("load_locations")
fi

# Load Crops
if ! exec_command "4/8" "Loading crops..." \
    "python manage.py load_crops sample_data/crops.csv"; then
    FAILED_COMMANDS+=("load_crops")
fi

# Load Crop Varieties
if ! exec_command "5/8" "Loading crop varieties..." \
    "python manage.py load_crop_varieties sample_data/crop_variety.csv"; then
    FAILED_COMMANDS+=("load_crop_varieties")
fi

# Load Crop Growth Stages
if ! exec_command "6/8" "Loading crop growth stages..." \
    "python manage.py load_crop_growth_stages sample_data/crop_growth_stages.csv"; then
    FAILED_COMMANDS+=("load_crop_growth_stages")
fi

# Load Pest Control Data
if ! exec_command "7/8" "Loading pest control data..." \
    "python manage.py load_pests sample_data/pest_control.csv"; then
    FAILED_COMMANDS+=("load_pests")
fi

# Upload Farm Shapefiles
echo -e "${YELLOW}[8/8]${NC} Uploading farm shapefiles..."
if [ -n "$CLEAR_FARMS" ]; then
    echo -e "${BLUE}Mode: Clear existing farms and import fresh${NC}"
    FARM_CMD="python manage.py upload_farms sample_data/farms.zip --mode $FARM_MODE $CLEAR_FARMS"
else
    case $FARM_MODE in
        skip)
            echo -e "${BLUE}Mode: Skip existing farms${NC}"
            ;;
        update)
            echo -e "${BLUE}Mode: Update existing farms${NC}"
            ;;
        create)
            echo -e "${BLUE}Mode: Create (fail on duplicates)${NC}"
            ;;
    esac
    FARM_CMD="python manage.py upload_farms sample_data/farms.zip --mode $FARM_MODE"
fi
echo -e "${BLUE}Running:${NC} $FARM_CMD"

if docker exec -it $CONTAINER_NAME bash -c "cd /pemostbackend && $FARM_CMD"; then
    echo -e "${GREEN}Success!${NC}\n"
else
    echo -e "${RED}Failed!${NC}\n"
    FAILED_COMMANDS+=("upload_farms")
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ ${#FAILED_COMMANDS[@]} -eq 0 ]; then
    echo -e "${GREEN}All data loaded successfully!${NC}"
    echo -e "\n${GREEN}You can now access the application with sample data.${NC}"
else
    echo -e "${RED}Some commands failed:${NC}"
    for cmd in "${FAILED_COMMANDS[@]}"; do
        echo -e "  ${RED}- $cmd${NC}"
    done
    echo -e "\n${YELLOW}Please check the error messages above and try running the failed commands manually.${NC}"
    exit 1
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Data loading completed!${NC}"
echo -e "${BLUE}========================================${NC}\n"
