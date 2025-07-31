#!/bin/bash
"""
Azure Setup Helper Script

This script helps set up Azure CLI and Azure Developer CLI for the AI Avatar project.
"""

echo "🚀 Azure Setup Helper for AI Avatar"
echo "=" * 50

# Function to check if user is logged in to Azure CLI
check_azure_cli_auth() {
    if az account show &>/dev/null; then
        echo "✅ Azure CLI is authenticated"
        current_sub=$(az account show --query "id" -o tsv)
        current_name=$(az account show --query "name" -o tsv)
        echo "📋 Current subscription: $current_name ($current_sub)"
        return 0
    else
        echo "❌ Azure CLI not authenticated"
        return 1
    fi
}

# Function to check if user is logged in to Azure Developer CLI
check_azd_auth() {
    if azd auth show &>/dev/null; then
        echo "✅ Azure Developer CLI is authenticated"
        return 0
    else
        echo "❌ Azure Developer CLI not authenticated"
        return 1
    fi
}

# Function to setup Azure CLI
setup_azure_cli() {
    echo ""
    echo "🔧 Setting up Azure CLI..."
    
    if ! check_azure_cli_auth; then
        echo "Please log in to Azure CLI:"
        az login
        
        if check_azure_cli_auth; then
            echo "✅ Azure CLI authentication successful"
        else
            echo "❌ Azure CLI authentication failed"
            return 1
        fi
    fi
    
    # List available subscriptions
    echo ""
    echo "📋 Available subscriptions:"
    az account list --query "[].{Name:name, SubscriptionId:id, State:state}" -o table
    
    # Prompt for subscription selection if multiple
    sub_count=$(az account list --query "length([])" -o tsv)
    if [ "$sub_count" -gt 1 ]; then
        echo ""
        read -p "Enter subscription ID to use (or press Enter to keep current): " sub_id
        if [ ! -z "$sub_id" ]; then
            az account set --subscription "$sub_id"
            echo "✅ Subscription set to: $(az account show --query name -o tsv)"
        fi
    fi
    
    return 0
}

# Function to setup Azure Developer CLI
setup_azd() {
    echo ""
    echo "🔧 Setting up Azure Developer CLI..."
    
    if ! check_azd_auth; then
        echo "Please log in to Azure Developer CLI:"
        azd auth login
        
        if check_azd_auth; then
            echo "✅ Azure Developer CLI authentication successful"
        else
            echo "❌ Azure Developer CLI authentication failed"
            return 1
        fi
    fi
    
    return 0
}

# Function to verify Azure Speech Services access
verify_speech_services() {
    echo ""
    echo "🎤 Verifying Azure Speech Services access..."
    
    if [ -f ".env" ]; then
        source .env
        
        if [ ! -z "$AZURE_SPEECH_KEY" ] && [ ! -z "$AZURE_SPEECH_REGION" ]; then
            echo "✅ Speech Services configuration found in .env"
            echo "📍 Region: $AZURE_SPEECH_REGION"
            echo "🔑 Key: ${AZURE_SPEECH_KEY:0:8}..."
            
            # Test the connection using our test script
            if [ -f "scripts/test_speech.py" ]; then
                echo "🧪 Testing Speech Services connection..."
                python scripts/test_speech.py
            fi
        else
            echo "⚠️  Speech Services not configured in .env file"
            echo "💡 Please add AZURE_SPEECH_KEY and AZURE_SPEECH_REGION to your .env file"
        fi
    else
        echo "⚠️  .env file not found"
        echo "💡 Copy .env.example to .env and configure your Azure credentials"
    fi
}

# Function to create Azure resources
create_speech_resource() {
    echo ""
    echo "🏗️  Azure Speech Services Resource Creation Helper"
    
    if ! check_azure_cli_auth; then
        echo "❌ Please authenticate with Azure CLI first"
        return 1
    fi
    
    read -p "Enter resource group name (or press Enter for 'ai-avatar-rg'): " rg_name
    rg_name=${rg_name:-ai-avatar-rg}
    
    read -p "Enter location (or press Enter for 'eastus'): " location
    location=${location:-eastus}
    
    read -p "Enter Speech Services resource name (or press Enter for 'ai-avatar-speech'): " speech_name
    speech_name=${speech_name:-ai-avatar-speech}
    
    echo ""
    echo "Creating Azure resources..."
    echo "📍 Resource Group: $rg_name"
    echo "🌍 Location: $location"
    echo "🎤 Speech Service: $speech_name"
    echo ""
    
    # Create resource group
    echo "Creating resource group..."
    az group create --name "$rg_name" --location "$location"
    
    # Create Speech Services resource
    echo "Creating Speech Services resource..."
    az cognitiveservices account create \
        --name "$speech_name" \
        --resource-group "$rg_name" \
        --kind "SpeechServices" \
        --sku "S0" \
        --location "$location" \
        --yes
    
    # Get the keys
    echo "Retrieving Speech Services keys..."
    key1=$(az cognitiveservices account keys list --name "$speech_name" --resource-group "$rg_name" --query "key1" -o tsv)
    endpoint=$(az cognitiveservices account show --name "$speech_name" --resource-group "$rg_name" --query "properties.endpoint" -o tsv)
    
    echo ""
    echo "✅ Azure Speech Services resource created successfully!"
    echo ""
    echo "📋 Configuration for .env file:"
    echo "AZURE_SPEECH_KEY=$key1"
    echo "AZURE_SPEECH_REGION=$location"
    echo "AZURE_SPEECH_ENDPOINT=$endpoint"
    echo "AZURE_RESOURCE_GROUP=$rg_name"
    echo ""
    echo "💡 Copy these values to your .env file"
}

# Main menu
show_menu() {
    echo ""
    echo "🔧 Azure Setup Options:"
    echo "1. Setup Azure CLI authentication"
    echo "2. Setup Azure Developer CLI authentication"
    echo "3. Verify Azure Speech Services configuration"
    echo "4. Create Azure Speech Services resource"
    echo "5. Show current authentication status"
    echo "6. Exit"
    echo ""
}

# Main script execution
main() {
    while true; do
        show_menu
        read -p "Select an option (1-6): " choice
        
        case $choice in
            1)
                setup_azure_cli
                ;;
            2)
                setup_azd
                ;;
            3)
                verify_speech_services
                ;;
            4)
                create_speech_resource
                ;;
            5)
                echo ""
                echo "🔍 Current Authentication Status:"
                check_azure_cli_auth
                check_azd_auth
                ;;
            6)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please select 1-6."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run the main function
main
