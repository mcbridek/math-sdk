#!/bin/bash
# Regenerate books without mode adjustments to match lookup tables

cd /Users/kmcbride/Documents/GitHub/se-beat_the_boss_math/math-sdk

# 1. Backup current game_override.py
cp games/beat_the_boss/game_override.py games/beat_the_boss/game_override.py.backup

# 2. Temporarily remove mode adjustments (use base multiplier only)
cat > games/beat_the_boss/game_override_temp.py << 'EOF'
# Temporarily use line 129 without adjustment for book generation
        multiplier = base_multiplier  # No mode adjustment for book generation
EOF

# Use sed to replace the adjustment block
sed -i.bak '127,134s/.*/        # Temporarily disabled: adjustment = getattr(self.config, '\''mode_rtp_adjustments'\'', {}).get(mode_name, 1.0)\n        multiplier = base_multiplier/' games/beat_the_boss/game_override.py

# 3. Regenerate books
source env/bin/activate
python games/beat_the_boss/run.py

# 4. Copy new books to publish_files
cp games/beat_the_boss/library/books/*.jsonl.zst games/beat_the_boss/library/publish_files/

# 5. Update index.json to reference books
cat > games/beat_the_boss/library/publish_files/index.json << 'EOF'
{
    "modes": [
        {
            "name": "macron",
            "cost": 1.0,
            "events": "books_macron.jsonl.zst",
            "weights": "lookUpTable_macron_0.csv"
        },
        {
            "name": "putin",
            "cost": 2.0,
            "events": "books_putin.jsonl.zst",
            "weights": "lookUpTable_putin_0.csv"
        },
        {
            "name": "trump",
            "cost": 3.0,
            "events": "books_trump.jsonl.zst",
            "weights": "lookUpTable_trump_0.csv"
        }
    ]
}
EOF

# 6. Restore original game_override.py
mv games/beat_the_boss/game_override.py.backup games/beat_the_boss/game_override.py

echo "Books regenerated without mode adjustments and copied to publish_files/"
echo "Upload files from: games/beat_the_boss/library/publish_files/"