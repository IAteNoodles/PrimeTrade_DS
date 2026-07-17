import csv, re, sys
from collections import defaultdict, Counter

outpath = r'C:\Users\Noodl\Projects\FindOut\data_gen\analysis_final.txt'

rows = []
with open(r'C:\Users\Noodl\Projects\FindOut\data_gen\dataset.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

nw = [r for r in rows if not re.search(r'\bWHERE\b', r.get('Cypher',''), re.IGNORECASE)]
nwo = [r for r in nw if re.search(r'\bORDER\s+BY\b', r.get('Cypher',''), re.IGNORECASE)]
nwono = [r for r in nw if not re.search(r'\bORDER\s+BY\b', r.get('Cypher',''), re.IGNORECASE)]

skip_words = {
    'I','A','An','The','This','That','These','Those','How','What','Which','Who','Where','When','Why',
    'Is','Are','Was','Were','Do','Does','Did','Can','Could','Would','Should','Has','Have','Had',
    'Will','Shall','May','Might','Must','In','On','At','To','For','With','By','From','Of','And',
    'But','Or','Not','No','If','Then','Each','Every','All','Both','Few','Many','Some','Any',
    'There','Here','Just','Only','Also','Very','Much','More','Less','Most','Such','Than','Too',
    'Now','Still','Even','Well','So','As','Be','Been','Its','Let','Make','None','Own','Per',
    'Put','Set','Their','Them','Through','Under','Until','Upon','Us','Via','We','Yet','Me','My',
    'He','She','It','They','His','Her','Our','Your','Am','About','Between','After','Before',
    'During','Since','Because','While','Although','Though','Unless','Whether','Into','Within',
    'Without','Against','Among','Throughout','According','Along','Across','Behind','Beside',
    'Beyond','Despite','Except','Inside','Near','Outside','Toward','Towards','Upon','Around',
    'Down','Off','Out','Over','Up','Like','Then','Else','Rather','Instead','Therefore','Thus',
    'However','Moreover','Furthermore','Nevertheless','Meanwhile','Otherwise',
    'Company','Employee','Customer','User','Artist','Student','Teacher','Player','Driver',
    'Team','City','State','Country','Department','Album','Movie','Episode','Paper','Book',
    'Product','Order','Transaction','Event','Patient','School','Station','Bank','Project',
    'Comment','Method','Match','Race','Game','Song','Track','Flight','Program','Course',
    'Category','Genre','Type','Status','Language','Industry','Position','Role',
    'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday',
    'Mondays','Tuesdays','Wednesdays','Thursdays','Fridays','Saturdays','Sundays',
    'January','February','March','April','May','June','July','August','September',
    'October','November','December',
}

categories = defaultdict(list)

for r in nwono:
    nl = r.get('NL','').strip()
    cy = r.get('Cypher','').strip()
    cats = []

    # (d) year_filter
    if re.search(r'\b(in|for|of|since|from|before|after|during)\s+(the\s+)?(19|20)\d{2}\b', nl, re.IGNORECASE):
        cats.append('year_filter')
    elif re.search(r'\b(19|20)\d{2}\b', nl):
        cats.append('year_filter')

    # (g) subquery
    if re.search(r'\baverage\b|\bmean\b|\bmedian\b', nl, re.IGNORECASE):
        cats.append('subquery')

    # (c) comparison - comprehensive
    if re.search(r'\bmore\s+than\b|\bless\s+than\b|\bfewer\s+than\b|\bgreater\s+than\b|\bhigher\s+than\b|\blower\s+than\b', nl, re.IGNORECASE):
        cats.append('comparison')
    elif re.search(r'\babove\b|\bbelow\b|\bat\s+least\b|\bexceeds?\b|\bexceeding\b', nl, re.IGNORECASE):
        cats.append('comparison')
    elif re.search(r'\bminimum\b|\bmaximum\b|\btop\s+\d|\bbottom\b', nl, re.IGNORECASE):
        cats.append('comparison')
    elif re.search(r'\bmost\b|\bleast\b', nl, re.IGNORECASE):
        cats.append('comparison')
    elif re.search(r'\bhighest\b|\blowest\b|\blargest\b|\bsmallest\b|\bbiggest\b|\bnewest\b|\boldest\b|\bfastest\b|\bslowest\b|\blongest\b|\bshortest\b', nl, re.IGNORECASE):
        cats.append('comparison')
    elif re.search(r'\bover\s+budget\b|\bunder\s+budget\b|\bin\s+debt\b|\bfirst\s+\d+\b', nl, re.IGNORECASE):
        cats.append('comparison')
    elif re.search(r'\bfrom\s+(id\s+)?\d+\s+to\s+\d+\b', nl, re.IGNORECASE):
        cats.append('comparison')

    # (b) cat_filter - comprehensive
    if re.search(r'\bgender\b|\bstatus\b|\btype\b|\bgenre\b|\bcategory\b|\bclass\b|\bkind\b|\bspecies\b|\bnationality\b|\bdepartment\b|\brole\b|\bposition\b|\boccupation\b|\bprofession\b|\bindustry\b|\blanguage\b|\breligion\b|\brace\b|\bethnicity\b', nl, re.IGNORECASE):
        cats.append('cat_filter')
    elif re.search(r'\bmale\b|\bfemale\b|\bactive\b|\binactive\b|\bmarried\b|\bsingle\b|\bdivorced\b|\balive\b|\bdead\b|\bdisabled\b|\benabled\b', nl, re.IGNORECASE):
        cats.append('cat_filter')
    elif re.search(r'\bcompleted\b|\bpending\b|\bapproved\b|\brejected\b|\bcancelled\b|\bclosed\b|\bopen\b|\bdiscontinued\b|\bsubscriber\b|\bsubcriber\b', nl, re.IGNORECASE):
        cats.append('cat_filter')
    elif re.search(r'\bnight\s+shift\b|\bday\s+shift\b|\binternationally\b|\bdomestic\b|\binternational\b', nl, re.IGNORECASE):
        cats.append('cat_filter')
    elif re.search(r'\branked\s+number\s+\d\b|\bplayoff\b|\bpost\s+season\b', nl, re.IGNORECASE):
        cats.append('cat_filter')

    # (a) name_match - refined
    has_quotes = bool(re.search(r'"[^"]+"', nl) or re.search(r"'[^']+'", nl))
    has_named = bool(re.search(r'\bnamed\b|\bcalled\b|\btitled\b', nl, re.IGNORECASE))
    
    if has_quotes:
        cats.append('name_match')
    elif has_named:
        cats.append('name_match')
    elif re.search(r'\babout\b\s+[A-Z]', nl, re.IGNORECASE):
        cats.append('name_match')
    else:
        words = nl.split()
        proper = []
        for i, w in enumerate(words):
            clean = w.rstrip('.,!?;:"\'')
            if i > 0 and len(clean) > 2 and clean[0].isupper() and clean not in skip_words:
                proper.append(clean)
        if proper:
            cats.append('name_match')

    # (e) prepositional
    loc_match = re.findall(r'(?:from|in)\s+([A-Z][a-z]+)', nl)
    non_year_locs = [l for l in loc_match if not re.match(r'(19|20)\d{2}', l)]
    if non_year_locs:
        cats.append('prepositional')

    # (f) compound
    if re.search(r'\bnot\b|\bwithout\b|\bnever\b|\bneither\b|\bnor\b', nl, re.IGNORECASE):
        cats.append('compound')
    elif re.search(r"\bdon'?t\b|\bdoesn'?t\b|\bdidn'?t\b|\bwasn'?t\b|\bweren'?t\b|\bisn'?t\b|\baren'?t\b|\bcannot\b|\bcan'?t\b", nl, re.IGNORECASE):
        cats.append('compound')
    elif re.search(r'\bunable\s+to\b', nl, re.IGNORECASE):
        cats.append('compound')
    elif re.search(r'\bno\s+\w+', nl, re.IGNORECASE):
        if not re.search(r'\bhow\s+many\b', nl, re.IGNORECASE):
            cats.append('compound')

    if not cats:
        cats.append('genuinely_no_filter')

    for c in cats:
        categories[c].append((r, cats[:]))

lines = []

# Summary stats
lines.append('=' * 70)
lines.append('DATASET ANALYSIS: Missing WHERE Clauses in Cypher Queries')
lines.append('=' * 70)
lines.append('')
lines.append(f'Total dataset rows: {len(rows)}')
lines.append(f'Rows with no WHERE clause: {len(nw)} ({len(nw)/len(rows)*100:.1f}%)')
lines.append(f'  ├─ No WHERE + has ORDER BY: {len(nwo)} (separate group)')
lines.append(f'  └─ No WHERE + no ORDER BY:  {len(nwono)} (analyzed below)')
lines.append('')

# Category breakdown
lines.append('=' * 70)
lines.append('MISSING FILTER CATEGORIES (602 rows: no WHERE, no ORDER BY)')
lines.append('=' * 70)
lines.append('')

cat_order = ['comparison','subquery','cat_filter','compound','year_filter','name_match','prepositional','genuinely_no_filter']
cat_descriptions = {
    'comparison': 'Superlatives or numeric comparisons (most/least/highest/biggest/at least/over/first N/range)',
    'subquery': 'NL mentions average/mean/median — implies aggregation needing subquery',
    'cat_filter': 'Categorical attribute values (male/female/active/discontinued/night shift/genre)',
    'compound': 'Negation or compound conditions (not/never/without/unable)',
    'year_filter': 'Year patterns (in 2016/for 2009/of 2018)',
    'name_match': 'Quoted strings, proper nouns, or "named/called/titled" patterns',
    'prepositional': '"from/in X" where X is a location/proper noun',
    'genuinely_no_filter': 'Simple counts/lists with no filter implication',
}

for cat in cat_order:
    items = [x[0] for x in categories[cat]]
    all_cats_list = [x[1] for x in categories[cat]]
    lines.append(f'--- {cat.upper()}: {len(items)} rows ---')
    lines.append(f'  Definition: {cat_descriptions[cat]}')
    lines.append('')
    lines.append(f'  Examples:')
    for i, ex in enumerate(items[:3]):
        nl = ex.get('NL','').strip()[:200]
        cy = ex.get('Cypher','').strip()[:140]
        lines.append(f'    {i+1}. NL: {nl}')
        lines.append(f'       CY: {cy}')
        other = [c for c in all_cats_list[i] if c != cat]
        if other:
            lines.append(f'       Also in: {other}')
        lines.append('')
    lines.append('')

# Multi-category overlap
row_id_cats = defaultdict(list)
for cat, items in categories.items():
    for r, rcats in items:
        row_id_cats[id(r)].append(cat)

multi = sum(1 for v in row_id_cats.values() if len(v) > 1)
single = sum(1 for v in row_id_cats.values() if len(v) == 1)

lines.append('=' * 70)
lines.append('OVERLAP ANALYSIS')
lines.append('=' * 70)
lines.append('')
lines.append(f'Unique rows: {len(row_id_cats)}')
lines.append(f'  In exactly 1 category: {single} ({single/len(row_id_cats)*100:.1f}%)')
lines.append(f'  In multiple categories: {multi} ({multi/len(row_id_cats)*100:.1f}%)')
lines.append('')

cooccur = Counter()
for rid, clist in row_id_cats.items():
    if len(clist) > 1:
        key = tuple(sorted(clist))
        cooccur[key] += 1

lines.append('Top category combinations (rows needing multiple fix types):')
for combo, cnt in cooccur.most_common(15):
    lines.append(f'  {" + ".join(combo)}: {cnt}')
lines.append('')

# Genuinely no filter deep dive
gnf = [x[0] for x in categories['genuinely_no_filter']]
lines.append('=' * 70)
lines.append(f'DEEP DIVE: genuinely_no_filter ({len(gnf)} rows)')
lines.append('=' * 70)
lines.append('')

gnf_patterns = Counter()
for r in gnf:
    nl = r.get('NL','').strip().lower()
    if re.search(r'\bhow\s+many\b', nl):
        gnf_patterns['how_many'] += 1
    elif re.search(r'\bcount\b|\bnumber\s+of\b|\btotal\s+number\b', nl):
        gnf_patterns['count/number_of'] += 1
    elif re.search(r'\blist\b|\bshow\b|\bfind\s+all\b', nl):
        gnf_patterns['list/show'] += 1
    elif re.search(r'\breturn\b|\bgive\b|\bwhat\s+is\b|\bwhat\s+are\b', nl):
        gnf_patterns['return/give/what_is'] += 1
    elif re.search(r'\bcalculate\b|\bcompute\b|\bfind\s+the\s+total\b', nl):
        gnf_patterns['calculate/compute'] += 1
    else:
        gnf_patterns['other'] += 1

lines.append('Sub-patterns in genuinely_no_filter:')
for k, v in gnf_patterns.most_common():
    lines.append(f'  {k}: {v}')
lines.append('')

lines.append('All genuinely_no_filter NL queries:')
for i, r in enumerate(gnf):
    nl = r.get('NL','').strip()
    cy = r.get('Cypher','').strip()[:120]
    lines.append(f'  {i+1}. {nl}')
    lines.append(f'     CY: {cy}')
lines.append('')

# ORDER BY section
lines.append('=' * 70)
lines.append(f'NO-WHERE BUT WITH ORDER BY: {len(nwo)} rows')
lines.append('=' * 70)
lines.append('')
lines.append('These rows have ORDER BY but no WHERE — they use sorting/limiting')
lines.append('instead of filtering. The NL queries almost always ask for')
lines.append('superlatives ("most", "fastest", "least", "highest").')
lines.append('')

nwo_cats = Counter()
for r in nwo:
    nl = r.get('NL','').strip().lower()
    if re.search(r'\bmost\b|\bleast\b|\bhighest\b|\blowest\b|\blargest\b|\bsmallest\b|\bbiggest\b|\bnewest\b|\boldest\b|\bfastest\b|\bslowest\b|\blongest\b|\bshortest\b|\btop\b|\bbest\b|\bworst\b', nl):
        nwo_cats['superlative'] += 1
    elif re.search(r'\bhow\s+many\b|\bcount\b|\bnumber\s+of\b', nl):
        nwo_cats['count'] += 1
    elif re.search(r'\blist\b|\bfind\b|\bshow\b|\bgive\b|\bwhat\b|\bwhich\b|\bwho\b', nl):
        nwo_cats['list_find_what_which'] += 1
    else:
        nwo_cats['other'] += 1

lines.append('ORDER BY row NL patterns:')
for k, v in nwo_cats.most_common():
    lines.append(f'  {k}: {v}')
lines.append('')

lines.append('Sample ORDER BY (no WHERE) rows:')
for ex in nwo[:10]:
    nl = ex.get('NL','').strip()[:180]
    cy = ex.get('Cypher','').strip()[:160]
    lines.append(f'  NL: {nl}')
    lines.append(f'  CY: {cy}')
    lines.append('')

# Final answer to question 5
lines.append('=' * 70)
lines.append('ANSWER TO: How many of the 1005 no-WHERE rows have ORDER BY?')
lines.append('=' * 70)
lines.append('')
lines.append(f'{len(nwo)} of the {len(nw)} no-WHERE rows have ORDER BY.')
lines.append(f'These are SEPARATE from the {len(nwono)} rows analyzed for missing filters.')
lines.append(f'{len(nwo)} = rows that use ORDER BY + LIMIT pattern (superlatives)')
lines.append(f'{len(nwono)} = rows with neither WHERE nor ORDER BY (missing filter analysis)')
lines.append(f'{len(nwo)} + {len(nwono)} = {len(nwo)+len(nwono)} = {len(nw)} ✓')

with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Final analysis written.')