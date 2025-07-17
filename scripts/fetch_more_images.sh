#!/bin/bash

echo "🔍 Fetching more missing images from Weave repository..."

# Counters
downloaded=0
failed=0

# Function to download an image
download_image() {
    local target_path="$1"
    local weave_path="$2"
    
    # Create directory if it doesn't exist
    target_dir=$(dirname "$target_path")
    if [ ! -d "$target_dir" ]; then
        mkdir -p "$target_dir"
        echo "  📁 Created directory: $target_dir"
    fi
    
    # Construct the GitHub raw URL
    url="https://raw.githubusercontent.com/wandb/weave/master/$weave_path"
    
    echo "  🔍 Fetching: $target_path"
    
    # Download the file
    if curl -s -o "$target_path" "$url"; then
        # Check if file is not empty and is a valid image
        if [ -s "$target_path" ] && file "$target_path" | grep -q "image"; then
            echo "  ✅ Downloaded: $target_path"
            ((downloaded++))
        else
            echo "  ❌ Failed (invalid file): $target_path"
            rm -f "$target_path"
            ((failed++))
        fi
    else
        echo "  ❌ Failed to download: $target_path"
        ((failed++))
    fi
}

# guides/core-types images
download_image "guides/core-types/imgs/leaderboard-example.png" "docs/docs/guides/core-types/imgs/leaderboard-example.png"
download_image "guides/core-types/imgs/cat-pumpkin-trace.png" "docs/docs/guides/core-types/imgs/cat-pumpkin-trace.png"
download_image "guides/core-types/imgs/audio-trace.png" "docs/docs/guides/core-types/imgs/audio-trace.png"
download_image "guides/core-types/imgs/prompt-object.png" "docs/docs/guides/core-types/imgs/prompt-object.png"
download_image "guides/core-types/imgs/prompt-comparison.png" "docs/docs/guides/core-types/imgs/prompt-comparison.png"

# guides/evaluation images
download_image "guides/evaluation/img/evals_tab.png" "docs/docs/guides/evaluation/img/evals_tab.png"
download_image "guides/evaluation/img/comparison.png" "docs/docs/guides/evaluation/img/comparison.png"
download_image "guides/evaluation/img/monitors-ui-1.png" "docs/docs/guides/evaluation/img/monitors-ui-1.png"
download_image "guides/evaluation/img/monitors-ui-2.png" "docs/docs/guides/evaluation/img/monitors-ui-2.png"
download_image "guides/evaluation/img/monitors-ui-3.png" "docs/docs/guides/evaluation/img/monitors-ui-3.png"
download_image "guides/evaluation/img/monitors-4.png" "docs/docs/guides/evaluation/img/monitors-4.png"

# guides/integrations images - Let's check for some common ones
download_image "guides/integrations/imgs/anthropic_trace.png" "docs/docs/guides/integrations/imgs/anthropic_trace.png"
download_image "guides/integrations/imgs/anthropic_ops.png" "docs/docs/guides/integrations/imgs/anthropic_ops.png"
download_image "guides/integrations/imgs/anthropic_model.png" "docs/docs/guides/integrations/imgs/anthropic_model.png"
download_image "guides/integrations/imgs/anthropic_tool.png" "docs/docs/guides/integrations/imgs/anthropic_tool.png"
download_image "guides/integrations/imgs/litellm_gif.gif" "docs/docs/guides/integrations/imgs/litellm_gif.gif"
download_image "guides/integrations/imgs/simple_llamaindex.png" "docs/docs/guides/integrations/imgs/simple_llamaindex.png"
download_image "guides/integrations/imgs/llamaindex_rag.png" "docs/docs/guides/integrations/imgs/llamaindex_rag.png"
download_image "guides/integrations/imgs/llamaindex_model.png" "docs/docs/guides/integrations/imgs/llamaindex_model.png"
download_image "guides/integrations/imgs/llamaindex_evaluation.png" "docs/docs/guides/integrations/imgs/llamaindex_evaluation.png"

echo ""
echo "✨ Done!"
echo "📊 Summary: $downloaded downloaded, $failed failed" 