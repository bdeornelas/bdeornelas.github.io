#!/bin/bash
set -e

# Build CSS and JS
npm run build
cp dist/css/style.css assets/css/style.min.css
cp dist/js/main.js assets/js/main.min.js

# Install Ruby dependencies
bundle install

# Create Vercel-specific config with dynamic URL
echo "url: https://$VERCEL_URL" > _config.vercel.yml

# Build Jekyll site
bundle exec jekyll build --config _config.yml,_config.vercel.yml

# Copy guideline files to _site for RAG access
cp -r claude-project-files _site/
cp ESC_GUIDELINES_TOC.md _site/

echo "Build completed successfully"
