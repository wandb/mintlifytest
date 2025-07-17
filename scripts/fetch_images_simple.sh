#!/bin/bash

echo "🔍 Fetching missing images from Weave repository..."

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

# guides/tracking images
download_image "guides/tracking/imgs/generators.png" "docs/docs/guides/tracking/imgs/generators.png"
download_image "guides/tracking/imgs/threadpoolexecutor.png" "docs/docs/guides/tracking/imgs/threadpoolexecutor.png"
download_image "guides/tracking/imgs/md-call-render.png" "docs/docs/guides/tracking/imgs/md-call-render.png"
download_image "guides/tracking/imgs/feedback_tab.png" "docs/docs/guides/tracking/imgs/feedback_tab.png"
download_image "guides/tracking/imgs/feedback_calls.png" "docs/docs/guides/tracking/imgs/feedback_calls.png"
download_image "guides/tracking/imgs/trace-tree-full.png" "docs/docs/guides/tracking/imgs/trace-tree-full.png"
download_image "guides/tracking/imgs/trace-tree-filter.png" "docs/docs/guides/tracking/imgs/trace-tree-filter.png"
download_image "guides/tracking/imgs/trace-tree-scrubbers.png" "docs/docs/guides/tracking/imgs/trace-tree-scrubbers.png"
download_image "guides/tracking/imgs/trace-tree-code-view.png" "docs/docs/guides/tracking/imgs/trace-tree-code-view.png"
download_image "guides/tracking/imgs/trace-tree-flame-view.png" "docs/docs/guides/tracking/imgs/trace-tree-flame-view.png"
download_image "guides/tracking/imgs/video-trace.png" "docs/docs/guides/tracking/imgs/video-trace.png"
download_image "guides/tracking/imgs/video-trace-popout.png" "docs/docs/guides/tracking/imgs/video-trace-popout.png"

# guides/tools images
download_image "guides/tools/imgs/open_chat_in_playground.png" "docs/docs/guides/tools/imgs/open_chat_in_playground.png"
download_image "guides/tools/imgs/playground_settings.png" "docs/docs/guides/tools/imgs/playground_settings.png"
download_image "guides/tools/imgs/playground_message_buttons.png" "docs/docs/guides/tools/imgs/playground_message_buttons.png"
download_image "guides/tools/imgs/playground_message_editor.png" "docs/docs/guides/tools/imgs/playground_message_editor.png"
download_image "guides/tools/imgs/playground_chat_input.png" "docs/docs/guides/tools/imgs/playground_chat_input.png"
download_image "guides/tools/imgs/saved-model.png" "docs/docs/guides/tools/imgs/saved-model.png"
download_image "guides/tools/imgs/saved-models-dropdown.png" "docs/docs/guides/tools/imgs/saved-models-dropdown.png"
download_image "guides/tools/imgs/comparison-2objs-sidebyside.png" "docs/docs/guides/tools/imgs/comparison-2objs-sidebyside.png"
download_image "guides/tools/imgs/comparison-2objs-unified.png" "docs/docs/guides/tools/imgs/comparison-2objs-unified.png"
download_image "guides/tools/imgs/comparison-2objs-baseline.png" "docs/docs/guides/tools/imgs/comparison-2objs-baseline.png"
download_image "guides/tools/imgs/comparison-2objs-baseline-set.png" "docs/docs/guides/tools/imgs/comparison-2objs-baseline-set.png"
download_image "guides/tools/imgs/comparison-2objs-reorder.png" "docs/docs/guides/tools/imgs/comparison-2objs-reorder.png"
download_image "guides/tools/imgs/comparison-2objs-numericdiffformat.png" "docs/docs/guides/tools/imgs/comparison-2objs-numericdiffformat.png"
download_image "guides/tools/imgs/comparison-2objs-numericdiffformat-updated.png" "docs/docs/guides/tools/imgs/comparison-2objs-numericdiffformat-updated.png"
download_image "guides/tools/imgs/comparsion-7objs-diffonly-subset.png" "docs/docs/guides/tools/imgs/comparsion-7objs-diffonly-subset.png"

echo ""
echo "✨ Done!"
echo "📊 Summary: $downloaded downloaded, $failed failed" 