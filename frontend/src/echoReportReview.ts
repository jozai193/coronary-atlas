// Source-text organisation only. No valve grades, coronary labels or numerical
// chamber measurements are inferred from prose or flattened OCR tables.
export interface EchoTextReview {structure:string[];valves:string[];flow:string[];impression:string[];warnings:string[]}
export function reviewEchoText(text:string):EchoTextReview {
  const review:EchoTextReview={structure:[],valves:[],flow:[],impression:[],warnings:[]}
  if(!/echocardiog|doppler|\bLVEF\b/i.test(text))return review
  let impression=false
  for(const raw of text.slice(0,50000).split(/\r?\n/)){
    const line=raw.trim();if(!line)continue
    if(/^impression\s*:/i.test(line)){impression=true;const tail=line.replace(/^impression\s*:\s*/i,'');if(tail)review.impression.push(tail);continue}
    if(impression){if(/^\[|^signature|^name of physician/i.test(line)){impression=false;continue}review.impression.push(line);continue}
    if(/^(?:aortic root|left ventri|right ventri|left atri|right atri|there is (?:normal|no pericardial)|IVC\b)/i.test(line)&&/\b(?:is|was|show|contractility|effusion)\b/i.test(line))review.structure.push(line)
    if(/\b(?:valve|annul(?:us|ar)|regurgitation)\b/i.test(line)&&!/\b(?:flow|gradient|velocity)\b/i.test(line))review.valves.push(line)
    if(/\b(?:flow pattern|regurgitant velocity|transaortic|peak gradient|mean gradient|valve area|PA pressure)\b/i.test(line))review.flow.push(line)
  }
  if(/\bNORMALS?\b/i.test(text)&&/\bDIMENSIONS?\b/i.test(text))review.warnings.push('Reference-range table detected. NORMAL/NORMALS values are not patient measurements. Blank cells and unreadable numbers remain unknown; check the image column by column.')
  if(review.impression.some(line=>/\bnormal\s+echo(?:cardiogram)?\b/i.test(line))&&[...review.structure,...review.valves].some(line=>/\b(?:dilated|stenosis|abnormal|reduced)\b/i.test(line)&&!/\b(?:no|not|without)\b/i.test(line)))review.warnings.push('Review wording: a normal echo impression appears alongside a specific finding such as dilation. Preserve both statements and ask the report author to clarify; no diagnosis is inferred.')
  if(review.structure.length||review.valves.length||review.flow.length||review.impression.length)review.warnings.push('These are OCR/pasted excerpts, not verified findings. Check missing or broken lines, negations, blank velocity/gradient fields and the original report. No coronary narrowing or model valve category is inferred.')
  return review
}

export function echoReviewNotes(review:EchoTextReview){return ([['Structure / chamber text',review.structure],['Impression text',review.impression],['Review reminders',review.warnings]] as const).filter(([,lines])=>lines.length).map(([heading,lines])=>`${heading}:\n${lines.join('\n')}`).join('\n\n')}
