#!/bin/bash

# Map of our directory structure to Weave's structure
declare -A PATH_MAPPINGS=(
    ["guides/tracking/imgs/"]="docs/docs/guides/tracking/imgs/"
    ["guides/core-types/imgs/"]="docs/docs/guides/core-types/imgs/"
    ["guides/integrations/imgs/"]="docs/docs/guides/integrations/imgs/"
    ["guides/evaluation/img/"]="docs/docs/guides/evaluation/img/"
    ["guides/tools/imgs/"]="docs/docs/guides/tools/imgs/"
)

# Counters
downloaded=0
skipped=0
failed=0

echo "🔍 Fetching missing images from Weave repository..."

# List of missing images and their locations
declare -A MISSING_IMAGES=(
    # guides/tracking images
    ["guides/tracking/imgs/generators.png"]="docs/docs/guides/tracking/imgs/generators.png"
    ["guides/tracking/imgs/threadpoolexecutor.png"]="docs/docs/guides/tracking/imgs/threadpoolexecutor.png"
    ["guides/tracking/imgs/md-call-render.png"]="docs/docs/guides/tracking/imgs/md-call-render.png"
    ["guides/tracking/imgs/feedback_tab.png"]="docs/docs/guides/tracking/imgs/feedback_tab.png"
    ["guides/tracking/imgs/feedback_calls.png"]="docs/docs/guides/tracking/imgs/feedback_calls.png"
    ["guides/tracking/imgs/trace-tree-full.png"]="docs/docs/guides/tracking/imgs/trace-tree-full.png"
    ["guides/tracking/imgs/trace-tree-filter.png"]="docs/docs/guides/tracking/imgs/trace-tree-filter.png"
    ["guides/tracking/imgs/trace-tree-scrubbers.png"]="docs/docs/guides/tracking/imgs/trace-tree-scrubbers.png"
    ["guides/tracking/imgs/trace-tree-code-view.png"]="docs/docs/guides/tracking/imgs/trace-tree-code-view.png"
    ["guides/tracking/imgs/trace-tree-flame-view.png"]="docs/docs/guides/tracking/imgs/trace-tree-flame-view.png"
    ["guides/tracking/imgs/video-trace.png"]="docs/docs/guides/tracking/imgs/video-trace.png"
    ["guides/tracking/imgs/video-trace-popout.png"]="docs/docs/guides/tracking/imgs/video-trace-popout.png"
    
    # guides/tools images
    ["guides/tools/imgs/open_chat_in_playground.png"]="docs/docs/guides/tools/imgs/open_chat_in_playground.png"
    ["guides/tools/imgs/playground_settings.png"]="docs/docs/guides/tools/imgs/playground_settings.png"
    ["guides/tools/imgs/playground_message_buttons.png"]="docs/docs/guides/tools/imgs/playground_message_buttons.png"
    ["guides/tools/imgs/playground_message_editor.png"]="docs/docs/guides/tools/imgs/playground_message_editor.png"
    ["guides/tools/imgs/playground_chat_input.png"]="docs/docs/guides/tools/imgs/playground_chat_input.png"
    ["guides/tools/imgs/saved-model.png"]="docs/docs/guides/tools/imgs/saved-model.png"
    ["guides/tools/imgs/saved-models-dropdown.png"]="docs/docs/guides/tools/imgs/saved-models-dropdown.png"
    ["guides/tools/imgs/comparison-2objs-sidebyside.png"]="docs/docs/guides/tools/imgs/comparison-2objs-sidebyside.png"
    ["guides/tools/imgs/comparison-2objs-unified.png"]="docs/docs/guides/tools/imgs/comparison-2objs-unified.png"
    ["guides/tools/imgs/comparison-2objs-baseline.png"]="docs/docs/guides/tools/imgs/comparison-2objs-baseline.png"
    ["guides/tools/imgs/comparison-2objs-baseline-set.png"]="docs/docs/guides/tools/imgs/comparison-2objs-baseline-set.png"
    ["guides/tools/imgs/comparison-2objs-reorder.png"]="docs/docs/guides/tools/imgs/comparison-2objs-reorder.png"
    ["guides/tools/imgs/comparison-2objs-numericdiffformat.png"]="docs/docs/guides/tools/imgs/comparison-2objs-numericdiffformat.png"
    ["guides/tools/imgs/comparison-2objs-numericdiffformat-updated.png"]="docs/docs/guides/tools/imgs/comparison-2objs-numericdiffformat-updated.png"
    ["guides/tools/imgs/comparsion-7objs-diffonly-subset.png"]="docs/docs/guides/tools/imgs/comparsion-7objs-diffonly-subset.png"
)

# Download each missing image
for target_path in "${!MISSING_IMAGES[@]}"; do
    weave_path="${MISSING_IMAGES[$target_path]}"
    
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
        # Check if file is not empty
        if [ -s "$target_path" ]; then
            echo "  ✅ Downloaded: $target_path"
            ((downloaded++))
        else
            echo "  ❌ Failed (empty file): $target_path"
            rm -f "$target_path"
            ((failed++))
        fi
    else
        echo "  ❌ Failed to download: $target_path"
        ((failed++))
    fi
done

echo ""
echo "✨ Done!"
echo "📊 Summary: $downloaded downloaded, $skipped skipped, $failed failed" 