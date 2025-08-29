#!/bin/bash

# ANSI color codes
PURPLE='\033[1;35m'
RED='\033[1;31m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

# Configuration
target_dir="$HOME/Github/agnosticd"
remote_url="origin"

# Function to display a message in green color
display_success() {
  echo -e "${GREEN}$1${NC}"
}

# Function to display an error message in red color
display_error() {
  echo -e "${RED}$1${NC}"
}

# Function to check if a tag exists locally
tag_exists_local() {
  git tag -l | grep -q "^$1$"
}

# Function to check if a tag exists remotely
tag_exists_remote() {
  git ls-remote --tags "$remote_url" | grep -q "refs/tags/$1"
}

# Function to check if the tag name is valid
is_valid_tag_name() {
  if [[ "$1" =~ ^[a-zA-Z0-9-]+-[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    return 0
  else
    return 1
  fi
}

# Function to remove the existing repository and clone it again
remove_and_clone_repository() {
  echo "Removing the existing repository..."
  rm -rf "$target_dir"
  git clone "https://github.com/redhat-cop/agnosticd.git" "$target_dir"
  display_success "Repository 'agnosticd' was successfully cloned."
}

# Check if the 'agnosticd' repository directory exists
if [ ! -d "$target_dir" ]; then
  echo "The 'agnosticd' repository does not exist in the target directory."
  read -p "Do you want to clone the repository? (yes/no): " confirm_clone
  case "$confirm_clone" in
    [Yy]|[Yy][Ee][Ss]) remove_and_clone_repository ;;
    *) echo "The script will abort. Please make sure the 'agnosticd' repository exists in the target directory." && exit 1 ;;
  esac
fi

# Change to the target directory
cd "$target_dir"

# Perform a git pull --rebase
display_success "Rebasing 'agD' repository..."
if ! git pull --rebase; then
  display_error "Error: Git pull --rebase failed."
  read -p "Do you want to remove the existing repository and clone it again? (yes/no): " confirm_remove
  case "$confirm_remove" in
    [Yy]|[Yy][Ee][Ss]) remove_and_clone_repository ;;
    *) display_error "The script will abort. Please fix the issues with the repository and try again." && exit 1 ;;
  esac
fi

# Perform a git pull with tags
if ! git pull --tags; then
  display_error "Error: Failed to pull tags. Please check your network connection and try again."
  exit 1
fi

# Function to check if a tag exists locally
tag_exists_local() {
  git tag -l | grep -q "^$1$"
}

# Function to check if a tag exists remotely
tag_exists_remote() {
  git ls-remote --tags "$remote_url" | grep -q "refs/tags/$1"
}

# Function to check if the tag name is valid
is_valid_tag_name() {
  if [[ "$1" =~ ^[a-zA-Z0-9-]+-[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    return 0
  else
    return 1
  fi
}

# Ask for the tag you want to create
while true; do
  read -p "Enter the tag you want to create: " tag

  # Validate the tag name format
  if is_valid_tag_name "$tag"; then
    break
  else
    display_error "Error: The tag name format is invalid. Please use a valid format (e.g., billys-test-tag-1.0.0) and try again."
  fi
done

# Check if the tag already exists locally
if tag_exists_local "$tag"; then
  display_error "Tag '$tag' already exists locally. Here's the information for the existing tag:"
  git log --tags --simplify-by-decoration --pretty=format:%ci%d | grep "tag: $tag"
  display_error "The script will abort. The tag won't be pushed to the origin."
elif tag_exists_remote "$tag"; then
  display_error "Tag '$tag' already exists in the remote repository. Here's the information for the existing remote tag:"
  git ls-remote --tags "$remote_url" | grep "refs/tags/$tag"
  display_error "The script will abort. The tag won't be pushed to the origin."
else
  # If the tag doesn't exist, create it
  git tag "$tag"
  display_success "Tag '$tag' created successfully."

  # Ask for confirmation before pushing the tag to the remote repository
  while true; do
    read -p "Do you want to push the tag to the origin? (yes/no): " confirm_push
    case "$confirm_push" in
      [Yy]|[Yy][Ee][Ss]) break ;;
      [Nn]|[Nn][Oo]) echo "Tag '$tag' was not pushed to origin."; exit 0 ;;
      *) display_error "Invalid input. Please enter 'yes' or 'no'." ;;
    esac
  done

  if ! git push "$remote_url" "$tag"; then
    display_error "Error: Failed to push the tag to the remote repository. Please check your network connection and try again."
    exit 1
  else
    display_success "Tag '$tag' pushed to origin successfully."

    # Check if the tag exists after the push and display the success message accordingly
    if tag_exists_remote "$tag"; then
      display_success "Tag '$tag' was successfully pushed to the remote repository."
    fi
  fi
fi

# Display the information for the tag (whether it exists or was just created)
echo "Information for the existing tag '$tag':"
git log --tags --simplify-by-decoration --pretty=format:%ci%d | grep "tag: $tag"

