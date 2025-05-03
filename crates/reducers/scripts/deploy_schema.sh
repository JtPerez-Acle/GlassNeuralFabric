#!/bin/bash
# Script to deploy the SpacetimeDB schema for GlassNeuralFabric

set -e  # Exit on error

# Default database name
DB_NAME="neurospace"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --db-name)
      DB_NAME="$2"
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [--db-name NAME] [--force]"
      echo ""
      echo "Options:"
      echo "  --db-name NAME  Name of the SpacetimeDB database (default: neurospace)"
      echo "  --force         Force recreation of the database if it exists"
      echo "  --help          Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if SpacetimeDB is installed
if ! command -v spacetimedb &> /dev/null; then
    echo "Error: SpacetimeDB is not installed"
    echo "Please install SpacetimeDB first: https://spacetimedb.com/docs/getting-started/installation"
    exit 1
fi

# Check if the database exists
if spacetimedb list | grep -q "$DB_NAME"; then
    if [[ "$FORCE" == "true" ]]; then
        echo "Database '$DB_NAME' exists, recreating..."
        spacetimedb delete "$DB_NAME" --force
    else
        echo "Error: Database '$DB_NAME' already exists"
        echo "Use --force to recreate the database"
        exit 1
    fi
fi

# Create the database
echo "Creating database '$DB_NAME'..."
spacetimedb create "$DB_NAME"

# Deploy the schema
echo "Deploying schema..."
spacetimedb sql "$DB_NAME" -f schema/schema.sql

echo "Schema deployed successfully to database '$DB_NAME'"
