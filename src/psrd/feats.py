import os
import json
import re
from BeautifulSoup import BeautifulSoup
from psrd.rules import write_rules
from psrd.files import char_replace
from psrd.universal import parse_universal
from psrd.sections import ability_pass, is_anonymous_section, has_subsections, entity_pass, find_section, quote_pass

def adjust_core_pass(struct, filename):
	first = 3
	second = 6
	if filename in ('advancedFeats.html', 'ultimateMagicFeats.html'):
		first = 2
	fdesc = struct['sections'][first]
	special = fdesc['sections'][second - 2]
	table = special['sections'][0]
	del special['sections']
	fdesc['sections'].insert(second - 1, table)
	feats = fdesc['sections'][second:]
	del fdesc['sections'][second:]
	sections = struct['sections']
	struct = sections.pop(0)
	struct['sections'] = sections
	return struct, feats

def adjust_ultimate_combat_pass(struct):
	first = 3
	second = 6
	table = struct['sections'][2]['sections'][0]
	fdesc = struct['sections'][first]
	fdesc['sections'].insert(second - 1, table)
	del struct['sections'][2]
	feats = fdesc['sections'][second:]
	del fdesc['sections'][second:]
	sections = struct['sections']
	struct = sections.pop(0)
	struct['sections'] = sections
	p = find_section(struct, name="Prerequisites", section_type='section')
	p['name'] = 'Prerequisite'
	return struct, feats

def adjust_advanced_class_guide_pass(struct):
	feats = struct['sections'][1]['sections'][5:]
	del struct['sections'][1]['sections'][5:]
	return struct, feats

def adjust_ultimate_campaign_pass(struct):
	feats = struct['sections'][2]['sections']
	del struct['sections'][2]
	return struct, feats

def adjust_mythic_adventures_pass(struct):
	feats = struct['sections'][2:]
	del struct['sections'][2:]
	return struct, feats

def adjust_feat_structure_pass(struct, filename):
	feats = []
	if filename in ('feats.html', 'advancedFeats.html', 'ultimateMagicFeats.html'):
		if struct['source'] == 'Advanced Class Guide':
			struct, feats = adjust_advanced_class_guide_pass(struct)
		else:
			struct, feats = adjust_core_pass(struct, filename)
	elif filename in ('monsterFeats.html'):
		feats = struct['sections']
		del struct['sections']
	elif filename in ('ultimateCombatFeats.html'):
		struct, feats = adjust_ultimate_combat_pass(struct)
	elif filename in ('storyFeats.html'):
		struct, feats = adjust_ultimate_campaign_pass(struct)
	elif filename in ('mythicFeats.html'):
		struct, feats = adjust_mythic_adventures_pass(struct)
	return struct, feats

def section_naming_pass(feat):
	p = find_section(feat, name="Prerequisite", section_type='section')
	if p != None:
		p['name'] = 'Prerequisites'
	b = find_section(feat, name="Benefit", section_type='section')
	if b != None:
		b['name'] = 'Benefits'
	p = find_section(feat, name="Prerequisites", section_type='section')
	if p != None:
		soup = BeautifulSoup(p['text'])
		p['description'] = ''.join(soup.findAll(text=True))
		del p['text']
	return feat

def prerequisite_pass(feat):
	p = find_section(feat, name="Prerequisites", section_type='section')
	if p != None:
		prereq = p['description']
		if prereq.endswith("."):
			prereq = prereq[:-1]
		if prereq.find(";") > -1:
			parts = prereq.split(";")
		else:
			parts = prereq.strip().split(", ")
		feat['prerequisites'] = [part.strip() for part in parts]

def feat_pass(feat):
	feat['type'] = 'feat'
	name = feat['name']
	m = re.search('(.*)\s*\((.*)\)', name)
	if m:
		newname = m.group(1).strip()
		types = m.group(2).split(", ")
		feat['name'] = newname
		feat['feat_types'] = types
	if not feat.has_key('text') and not feat.has_key('description'):
		for section in feat['sections']:
			if is_anonymous_section(section) and not has_subsections(section):
				feat['text'] = section['text']
				feat['sections'].remove(section)
	if feat.has_key('text') and not feat.has_key('description'):
		soup = BeautifulSoup(feat['text'])
		feat['description'] = ''.join(soup.findAll(text=True))
		del feat['text']

def monster_feat_pass(feat):
	types = feat.setdefault('feat_types', [])
	types.append("Monster")

def parse_feats(filename, output, book):
	struct = parse_universal(filename, output, book)
	struct = quote_pass(struct)
	struct = entity_pass(struct)
	rules, feats = adjust_feat_structure_pass(struct, os.path.basename(filename))

	for feat in feats:
		feat_pass(feat)
		ability_pass(feat)
		section_naming_pass(feat)
		prerequisite_pass(feat)
		if rules['name'] == 'Monster Feats':
			monster_feat_pass(feat)

	for feat in feats:
		print "%s: %s" %(feat['source'], feat['name'])
		filename = create_feat_filename(output, book, feat)
		fp = open(filename, 'w')
		json.dump(feat, fp, indent=4)
		fp.close()
	if rules:
		write_rules(output, rules, book, "feats")

def create_feat_filename(output, book, feat):
	title = char_replace(book) + "/feats/" + char_replace(feat['name'])
	return os.path.abspath(output + "/" + title + ".json")

