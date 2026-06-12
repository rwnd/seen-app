#!/usr/bin/env python3
"""Generate archetypes.json from embedded reference data. Run once or after bulk edits."""

import json
from pathlib import Path

IMAGE_STYLE = (
    "cinematic graphic novel, ink illustration, dramatic shadows, "
    "no speech bubbles, no text"
)

CATEGORIES = [
    "Leaders",
    "Advocates",
    "Enthusiasts",
    "Givers",
    "Architects",
    "Producers",
    "Creators",
    "Seekers",
    "Fighters",
    "Individualist",
]

# slug, name, category, tagline, core_wound, description, image_direction,
# primary_question_key, primary_question_text, extra questions dict
ARCHETYPE_DATA = [
    (
        "commander", "Commander", "Leaders",
        "Driven to achieve goals through determination and high standards",
        "Confuses control with care; equates softness with weakness",
        "Commanders are driven to achieve goals through determination and holding themselves and others to high standards of performance.",
        "A lone general standing in an empty war room, maps on the table, no one left to command, single light source",
        "fear",
        "When was the last time you let someone see you lose — and what did it cost you to hide it?",
        {
            "identity": "What does being a Commander feel like from the inside — what quality in yourself are you most proud of that others rarely see?",
            "memory": "Describe a moment when your determination either saved something important — or cost you something you didn't expect to lose.",
            "unsaid": "What do you know about yourself as a leader that you have never admitted out loud, even to yourself?",
        },
    ),
    (
        "shaper", "Shaper", "Leaders",
        "Visualizes ambitious goals and pushes through relentlessly",
        "Self-worth is entirely fused with the magnitude of their output",
        "Shapers visualize ambitious goals and push through obstacles with relentless drive, measuring themselves by the scale of what they build.",
        "A sculptor chiseling away at a statue that keeps growing larger than the room",
        "fear",
        "What are you building right now that you secretly suspect you're doing to prove something — not because you actually want it?",
        {
            "identity": "When you picture your best self, what are you holding in your hands — and who is watching?",
            "memory": "Describe a project you pushed through that proved something to you — and whether it was worth what it took.",
            "unsaid": "What would you have to admit if your current ambition failed tomorrow?",
        },
    ),
    (
        "quietleader", "Quiet Leader", "Leaders",
        "Leads through open-mindedness and equanimity",
        "Carries enormous internal clarity that almost never gets spoken aloud",
        "Quiet Leaders lead through open-mindedness and equanimity, guiding others with calm presence rather than forceful direction.",
        "A lighthouse, fully lit, surrounded by fog — ships guided but never seeing the source",
        "fear",
        "What is something true about your situation that you have fully understood but never said out loud to anyone — and why haven't you said it?",
        {
            "identity": "What quality of stillness in yourself do you trust most when everything around you is loud?",
            "memory": "Describe a time your quiet leadership changed an outcome — and whether anyone knew it was you.",
            "unsaid": "What would change in your life if you spoke with half the clarity you think with?",
        },
    ),
    (
        "inspirer", "Inspirer", "Advocates",
        "Motivates people to get behind challenging ideas",
        "Believes in the vision so hard they forget to check if others actually followed",
        "Inspirers motivate people to get behind challenging ideas, carrying conviction that can outpace the room's actual commitment.",
        "A conductor mid-symphony, turning to find half the orchestra has left their chairs",
        "fear",
        "Who are you inspiring right now who you secretly fear isn't as committed as you need them to be?",
        {
            "identity": "What part of you lights up when someone finally grasps the vision you've been carrying?",
            "memory": "Describe a moment you rallied people — and the first sign you weren't sure they were with you.",
            "unsaid": "What would you stop doing if you couldn't inspire anyone this week?",
        },
    ),
    (
        "campaigner", "Campaigner", "Advocates",
        "Rallies others around ideas and achieves practical results",
        "Momentum becomes identity; stopping feels like dying",
        "Campaigners rally others around ideas and drive toward practical results, often finding that motion itself becomes who they are.",
        "A lone figure still holding a banner in an empty field after the crowd has gone",
        "fear",
        "What cause or mission are you still fighting for that you privately wonder if you even believe in anymore?",
        {
            "identity": "What does momentum feel like in your body when a cause is actually working?",
            "memory": "Describe a campaign that succeeded — and whether you felt emptied or alive afterward.",
            "unsaid": "Who would you be if you stopped campaigning for six months?",
        },
    ),
    (
        "coach", "Coach", "Advocates",
        "Focused on self-growth, development and teaching others",
        "Identity built entirely around being needed; forgets their own needs exist",
        "Coaches are focused on growth, development, and teaching others — often building identity around being the one who holds things together.",
        "A pair of hands holding up a growing tree, roots slowly wrapping around the wrists",
        "fear",
        "Think of the person you're currently carrying the most weight for. What part of yourself have you quietly set aside to make room for them?",
        {
            "identity": "What do you love most about watching someone else grow — and when did you last feel that for yourself?",
            "memory": "Describe a time you coached someone brilliantly and neglected yourself in the same week.",
            "unsaid": "What need of yours have you reframed as 'just helping others'?",
        },
    ),
    (
        "promoter", "Promoter", "Enthusiasts",
        "Outgoing, charismatic, skilled with people",
        "The performance of enthusiasm can become a prison — exhausting to maintain, terrifying to drop",
        "Promoters are outgoing and charismatic, skilled at energizing rooms — but the performance of enthusiasm can become exhausting to maintain.",
        "A stage with one spotlight still lit, audience gone, performer sitting at the edge",
        "fear",
        "When you are completely alone and the performance is off — what does the silence feel like?",
        {
            "identity": "What version of you shows up when you don't have to win anyone over?",
            "memory": "Describe a time the room went quiet and you weren't sure who you were without the applause.",
            "unsaid": "What would people think if they saw you on a day you couldn't perform?",
        },
    ),
    (
        "impresario", "Impresario", "Enthusiasts",
        "Entertains, engages socially, facilitates great experiences",
        "Confuses the quality of the experience they create with the quality of their own worth",
        "Impresarios entertain, engage socially, and facilitate memorable experiences — sometimes mistaking the quality of what they create for their own worth.",
        "An empty banquet hall, perfectly set, waiting for guests who may not come",
        "fear",
        "What would happen to your relationships if you stopped making things memorable for people?",
        {
            "identity": "When you create a perfect evening for others, what are you hoping they'll feel about you?",
            "memory": "Describe an event you orchestrated that went beautifully — and how you felt when everyone left.",
            "unsaid": "Who would still want you around if you offered nothing but your presence?",
        },
    ),
    (
        "entertainer", "Entertainer", "Enthusiasts",
        "Creates experiences and engages with the world",
        "Humor and performance as armor — the joke is always ready before the vulnerability can surface",
        "Entertainers create experiences and engage with the world through performance — often with humor ready before vulnerability can surface.",
        "A jester mask hanging on a nail, the face behind it blurred and undefined",
        "fear",
        "What's the thing you deflect with a laugh that, if you sat with it quietly, would actually break you open?",
        {
            "identity": "What do you feel when the room is laughing — and what do you feel when the room goes quiet?",
            "memory": "Describe a moment you made everyone laugh and went home feeling hollow.",
            "unsaid": "What truth have you never told because you always had a punchline ready?",
        },
    ),
    (
        "peacekeeper", "Peacekeeper", "Givers",
        "Develops positive relationships, seeks harmony and cooperation",
        "Conflict-avoidance masquerading as kindness; they disappear themselves to keep the room comfortable",
        "Peacekeepers develop positive relationships and seek harmony, sometimes disappearing themselves to keep rooms comfortable.",
        "A bridge over turbulent water, perfectly maintained, slightly cracked at the center",
        "fear",
        "What do you actually think — about a situation you've been nodding through — that you have never let yourself say?",
        {
            "identity": "When harmony is restored, what part of you feels most relieved — and what part feels most erased?",
            "memory": "Describe a time you kept the peace and lost something true about yourself in the process.",
            "unsaid": "What disagreement are you avoiding that would actually set you free?",
        },
    ),
    (
        "problemsolver", "Problem Solver", "Givers",
        "Supports and helps others in an industrious, professional way",
        "Helping is safe; being helped is terrifying — receiving care feels like losing ground",
        "Problem Solvers support others industriously and professionally — finding that helping is safe while being helped feels like losing ground.",
        "A toolbox overflowing, the hands holding it bleeding slightly at the palms",
        "fear",
        "Who in your life keeps offering you something — support, rest, help — that you keep refusing? What are you protecting by refusing it?",
        {
            "identity": "What problem do you solve for others that you wish someone would solve for you?",
            "memory": "Describe a time you fixed everything for everyone and collapsed when no one noticed.",
            "unsaid": "What would it cost your identity to let someone take care of you?",
        },
    ),
    (
        "helper", "Helper", "Givers",
        "Compassion, care, support of emotional needs",
        "Love expressed through service rather than presence — giving so no one looks too closely at what they need",
        "Helpers express love through service and emotional care — giving so generously that no one looks too closely at what they need.",
        "An open door with warm light spilling out, the person standing just outside it, never stepping in",
        "fear",
        "If the person you love most could only receive one true thing from you — not help, not effort, just you — what would that be, and why is it so hard to give?",
        {
            "identity": "When you help someone, what do you hope they'll never have to see about you?",
            "memory": "Describe a time you gave everything you had and still felt unseen.",
            "unsaid": "What do you need that you've disguised as generosity?",
        },
    ),
    (
        "strategist", "Strategist", "Architects",
        "Generates and translates concepts into effective strategies",
        "Intelligence used as distance — thinking about the problem instead of feeling it",
        "Strategists generate concepts and translate them into effective strategies — sometimes using intelligence as distance from feeling.",
        "An intricate chessboard fully solved, the player staring at it, unable to make the first move",
        "fear",
        "What is the thing in your life you have analyzed perfectly and acted on least — and what does that gap tell you?",
        {
            "identity": "When you see the whole board clearly, what feeling do you push aside to keep thinking?",
            "memory": "Describe a strategy you mapped brilliantly that you never had the courage to execute.",
            "unsaid": "What are you afraid would happen if you stopped analyzing and simply moved?",
        },
    ),
    (
        "planner", "Planner", "Architects",
        "Structure, systems, translating ideas into plans",
        "Certainty addiction — the plan is a defense against the terror of irreversible action",
        "Planners create structure and systems, translating ideas into plans — sometimes using certainty as defense against irreversible action.",
        "An architect's blueprints spread across a table, the foundation already crumbling beneath it",
        "fear",
        "What are you still planning that would feel unsafe even if everything went exactly right?",
        {
            "identity": "What does a perfect plan give you that acting never could?",
            "memory": "Describe a plan you refined for months that became a reason never to begin.",
            "unsaid": "What decision are you postponing by calling it 'not ready yet'?",
        },
    ),
    (
        "orchestrator", "Orchestrator", "Architects",
        "Brings people together and mobilizes resources",
        "Invisible to themselves in their own system — so focused on moving pieces they forget they're a piece too",
        "Orchestrators bring people together and mobilize resources — so focused on moving pieces they forget they're a piece too.",
        "The center of a clock mechanism, every gear turning, the center axle standing perfectly still and alone",
        "fear",
        "In all the systems and people you're organizing right now — where do you actually fit? Not as a role. As a person.",
        {
            "identity": "When everything is coordinated, where do you stand in the picture you've built?",
            "memory": "Describe a time you held everything together and realized no one was holding you.",
            "unsaid": "What would fall apart if you stopped orchestrating for one week?",
        },
    ),
    (
        "implementer", "Implementer", "Producers",
        "Organizes and structures people and processes to execute",
        "Execution as escape — staying busy means never having to ask if this is what they actually want",
        "Implementers organize people and processes to execute — staying busy can mean never asking if this is what they actually want.",
        "A long corridor of open doors, each completed and closed, one door at the end slightly ajar",
        "fear",
        "If you stopped executing for 30 days and could only think — what question would surface that you've been too busy to ask yourself?",
        {
            "identity": "What does finishing something feel like — relief, proof, or escape?",
            "memory": "Describe a project you executed flawlessly that left you wondering why you did it.",
            "unsaid": "What desire have you buried under the next task list?",
        },
    ),
    (
        "investigator", "Investigator", "Producers",
        "Researches and analyzes to build knowledge",
        "The need to fully understand before acting — knowledge as permission they never quite grant themselves",
        "Investigators research and analyze to build knowledge — needing to fully understand before acting, as if knowledge were permission they never grant.",
        "A researcher at a desk surrounded by answered questions, one small blank piece of paper in the center",
        "fear",
        "What have you researched deeply and known clearly for a long time — and still not acted on? What are you still looking for?",
        {
            "identity": "When you learn something new, what old question does it quiet — and for how long?",
            "memory": "Describe the moment you knew enough to act and chose to read one more article instead.",
            "unsaid": "What permission are you waiting for that only you can give?",
        },
    ),
    (
        "technician", "Technician", "Producers",
        "Breaks down, analyzes and solves problems technically",
        "Precision as protection — if the mechanism is perfect, the human messiness around it can be ignored",
        "Technicians break down and solve problems technically — using precision as protection from human messiness.",
        "A perfectly calibrated machine with one organic element — a leaf, a hand — that keeps disrupting it",
        "fear",
        "What problem in your life cannot be solved technically — and how long have you been pretending it can?",
        {
            "identity": "When the system works perfectly, what human variable still unsettles you?",
            "memory": "Describe a time you fixed the mechanism and the relationship still broke.",
            "unsaid": "What mess in your life are you treating as a technical problem?",
        },
    ),
    (
        "adventurer", "Adventurer", "Creators",
        "Seeks fun, exciting, adventurous activities",
        "Motion as avoidance — as long as you're moving, you never have to arrive anywhere that requires you to stay",
        "Adventurers seek excitement and new experiences — motion as avoidance of arriving somewhere that requires them to stay.",
        "A map covered in routes and pins, one location circled and never visited",
        "fear",
        "What would you have to confront about yourself if you stopped moving and stayed in one place for a year?",
        {
            "identity": "What does the next adventure promise you that the present cannot?",
            "memory": "Describe a trip or thrill that was supposed to change you — and what stayed the same when you returned.",
            "unsaid": "What are you running toward that is actually something you're running from?",
        },
    ),
    (
        "artisan", "Artisan", "Creators",
        "Uses creativity to bring beautiful, well-crafted ideas to life",
        "The work is never quite finished — because finished means judged, and judged means exposed",
        "Artisans use creativity to craft beautiful work — often keeping pieces unfinished because finished means judged, and judged means exposed.",
        "A painting covered by a cloth in a lit gallery, every other piece on the walls",
        "fear",
        "What is something you've made — or almost made — that you've kept from the world? What are you protecting it from?",
        {
            "identity": "When you refine one more detail, what judgment are you postponing?",
            "memory": "Describe something you nearly released and pulled back at the last moment.",
            "unsaid": "What would it mean about you if the work were seen and found ordinary?",
        },
    ),
    (
        "inventor", "Inventor", "Creators",
        "Generates new and innovative ideas, products and solutions",
        "The next idea is always more exciting than the current one — completion is a kind of grief",
        "Inventors generate innovative ideas and solutions — often finding the next idea more exciting than completing the current one.",
        "A workbench covered in brilliant half-finished inventions, one window looking out on the world",
        "fear",
        "What idea have you had — repeatedly, for years — that you have never committed to? What keeps making it feel 'not quite right yet'?",
        {
            "identity": "When a new idea arrives, what does it save you from feeling about the old one?",
            "memory": "Describe an invention or project you abandoned the moment something shinier appeared.",
            "unsaid": "What would you lose if you finished one thing completely?",
        },
    ),
    (
        "explorer", "Explorer", "Seekers",
        "Seeks new knowledge and experiences with intrinsic motivation",
        "Possibility addiction — commitment feels like the death of the self that might have been something else",
        "Explorers seek new knowledge and experiences — sometimes treating commitment as the death of selves they might have become.",
        "A crossroads with ten paths visible, footprints going a few steps down each one, returning to center",
        "fear",
        "What would you lose — about who you think you are — if you finally committed to one path and stopped leaving exits open?",
        {
            "identity": "What does an open door represent to you — freedom, or a way to never be found?",
            "memory": "Describe a path you walked far enough to know it was right — and still walked away.",
            "unsaid": "Which version of yourself are you protecting by never fully choosing?",
        },
    ),
    (
        "thinker", "Thinker", "Seekers",
        "Takes an abstract, philosophical approach to problems",
        "Living in the mind as a way of avoiding the body and its inconvenient demands",
        "Thinkers take abstract, philosophical approaches — living in the mind as a way of avoiding the body's inconvenient demands.",
        "A figure standing at the edge of a cliff, perfectly calm, a storm raging behind them they haven't noticed",
        "fear",
        "What truth have you arrived at philosophically that your actual daily life completely contradicts?",
        {
            "identity": "When you understand something completely in theory, what part of living it frightens you?",
            "memory": "Describe an insight that changed how you think but not how you act.",
            "unsaid": "What would your body say if your mind stopped speaking for it?",
        },
    ),
    (
        "growthseeker", "Growth Seeker", "Seekers",
        "Deep passion for learning and personal development",
        "Growth as identity — if you stop improving, who are you? The pursuit can become another form of running",
        "Growth Seekers have deep passion for learning and development — sometimes making improvement itself another form of running.",
        "A garden tended obsessively, every plant staked and pruned, one wild bloom in the corner left alone",
        "fear",
        "What part of yourself have you been trying to fix or improve for so long that you've forgotten it might just be who you are?",
        {
            "identity": "When you improve something about yourself, what old self are you trying to leave behind?",
            "memory": "Describe a growth goal that became more important than the life you were living.",
            "unsaid": "What if you didn't need to become anyone else — what would you do with that freedom?",
        },
    ),
    (
        "protector", "Protector", "Fighters",
        "Upholds traditions, rules, standards, and personal duty",
        "The rules they protect so fiercely are sometimes protecting them from having to change",
        "Protectors uphold traditions, rules, and standards — sometimes using duty as protection from having to change.",
        "An old wall, beautifully maintained, the landscape it was built to protect long since changed around it",
        "fear",
        "What is something you have defended strongly — a belief, a standard, a way of doing things — that you have privately started to doubt?",
        {
            "identity": "What do you protect that also protects you from having to grow?",
            "memory": "Describe a time you held the line and wondered afterward who it was really for.",
            "unsaid": "What rule would you break if no one you respect was watching?",
        },
    ),
    (
        "enforcer", "Enforcer", "Fighters",
        "Engages through standards, rules, and traditions",
        "Standards as a measuring stick they inevitably hold against themselves first",
        "Enforcers engage through standards and rules — inevitably holding the measuring stick against themselves first.",
        "A judge's scale, perfectly balanced, with one small stone hidden under the judge's own side",
        "fear",
        "By your own standards — the ones you hold others to — where are you currently failing yourself, and what have you told yourself about why that's different?",
        {
            "identity": "When you enforce a standard, whose approval are you secretly seeking?",
            "memory": "Describe a time you held someone accountable and recognized the same flaw in yourself.",
            "unsaid": "What standard do you enforce in others because you can't enforce it in yourself?",
        },
    ),
    (
        "critic", "Critic", "Fighters",
        "Expresses opinions and debates perspectives",
        "The sharpest critiques are often the ones they haven't yet aimed inward",
        "Critics express opinions and debate perspectives — often wielding sharpest critiques they haven't yet aimed inward.",
        "A mirror cracked at the center, reflecting everything perfectly except the face looking into it",
        "fear",
        "What critique do you give others frequently that, if you turned it fully on yourself, would be the most uncomfortable thing you could hear?",
        {
            "identity": "When you spot what's wrong, what does that clarity protect you from feeling?",
            "memory": "Describe a critique you gave that landed true — and stung because you recognized yourself.",
            "unsaid": "What flaw in yourself do you keep finding in other people?",
        },
    ),
    (
        "individualist", "Individualist", "Individualist",
        "Marches to their own beat with unique self-expression",
        "Originality as armor — being different is safe; being ordinary and vulnerable is terrifying",
        "Individualists march to their own beat with unique self-expression — sometimes using originality as armor against ordinary vulnerability.",
        "A figure walking a completely unique path through a field, glancing sideways at the ordinary road they've been avoiding",
        "fear",
        "Underneath the part of you that insists on being different — what do you want that is embarrassingly simple and ordinary?",
        {
            "identity": "What part of being different feels most authentically you — and what part is performance?",
            "memory": "Describe a time you chose the unique path and secretly wished someone would walk it with you.",
            "unsaid": "What ordinary desire have you disguised as individuality?",
        },
    ),
]


def build_archetypes() -> dict:
    archetypes = {}
    for row in ARCHETYPE_DATA:
        slug, name, category, tagline, wound, desc, img_dir, primary_key, primary_q, extras = row
        questions = dict(extras)
        questions[primary_key] = primary_q
        archetypes[slug] = {
            "name": name,
            "category": category,
            "slug": slug,
            "tagline": tagline,
            "core_wound": wound,
            "description": desc,
            "questions": questions,
            "image_direction": img_dir,
            "image_style": IMAGE_STYLE,
        }
    return {
        "_comment": "Edit this file directly or run scripts/generate_archetypes.py. See docs/EDITING_DATA.md",
        "categories": CATEGORIES,
        "archetypes": archetypes,
    }


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "archetypes.json"
    out.write_text(json.dumps(build_archetypes(), indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {out} ({len(ARCHETYPE_DATA)} archetypes)")


if __name__ == "__main__":
    main()
