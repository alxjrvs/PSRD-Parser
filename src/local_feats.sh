#!/bin/bash
source dir.conf
./feat_parse.py -o $DATA_DIR -b "Core Rulebook"           $WEB_DIR/pathfinderRPG/prd/feats.html
./feat_parse.py -o $DATA_DIR -b "Bestiary"                $WEB_DIR/pathfinderRPG/prd/monsters/monsterFeats.html
#./feat_parse.py -o $DATA_DIR -b "Bestiary 2"                $WEB_DIR/pathfinderRPG/prd/additionalMonsters/monsterFeats.html
./feat_parse.py -o $DATA_DIR -b "Advanced Player's Guide" $WEB_DIR/pathfinderRPG/prd/advanced/advancedFeats.html
./feat_parse.py -o $DATA_DIR -b "Ultimate Magic"          $WEB_DIR/pathfinderRPG/prd/ultimateMagic/ultimateMagicFeats.html
./feat_parse.py -o $DATA_DIR -b "Ultimate Combat"         $WEB_DIR/pathfinderRPG/prd/ultimateCombat/ultimateCombatFeats.html

