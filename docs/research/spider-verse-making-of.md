# How the Spider-Verse films were made

Source notes, 2026-09-27. Covers *Spider-Man: Into the Spider-Verse* (2018) and *Spider-Man: Across the Spider-Verse* (2023): who made them, the ideas behind their look, and techniques we can borrow. Compiled from interviews, studio posts and press coverage; claims link to their sources. The [dinner montage study](../../apps/stop-motion/projects/spider-verse-dinner-montage/README.md) applies them to one scene. Return to the [research index](README.md).

## Who made them

- **Studios.** Sony Pictures Animation produced both films and Sony Pictures Imageworks animated them. Phil Lord and Christopher Miller wrote and produced both and pushed for a comic book brought to life.
- ***Into the Spider-Verse.*** Directed by Bob Persichetti, Peter Ramsey and Rodney Rothman. Production designer **Justin K. Thompson** defined the look and won the Annie Award for it ([Wikipedia](https://en.wikipedia.org/wiki/Justin_K._Thompson)). Danny Dimian was VFX supervisor ([VFX Voice](https://vfxvoice.com/imageworks-artists-break-the-mold-to-create-an-alternate-spider-verse/)) and Josh Beveridge head of character animation ([CG Spectrum](https://www.cgspectrum.com/blog/spider-man-into-the-spider-verse-how-they-got-that-mind-blowing-look)). Alberto Mielgo contributed early visual development. The film won the Academy Award for Best Animated Feature.
- ***Across the Spider-Verse.*** Directed by Joaquim Dos Santos, Kemp Powers and Thompson ([Wikipedia](https://en.wikipedia.org/wiki/Spider-Man:_Across_the_Spider-Verse)). Patrick O'Keefe was production designer, Dean Gordon art director and Mike Lasker VFX supervisor ([Screen Rant](https://screenrant.com/spider-man-across-the-spider-verse-clip-gwen-stacy/)). Pav Grochola, effects and look supervisor, led the line work and watercolor tools ([befores & afters](https://beforesandafters.com/2024/01/10/giving-spider-man-across-the-spider-verse-that-crucial-hand-made-quality/)).
- **Scale.** The first film had about 800 people and more than 2,600 shots ([CG Spectrum](https://www.cgspectrum.com/blog/spider-man-into-the-spider-verse-how-they-got-that-mind-blowing-look)), with over 150 animators, Imageworks' largest team at the time ([VFX Voice](https://vfxvoice.com/imageworks-artists-break-the-mold-to-create-an-alternate-spider-verse/)). The sequel had about 1,000 artists working for almost two years, around 240 characters and six styled universes; Miller calls it the largest crew of any animated film ([CBR](https://www.cbr.com/spider-man-across-the-spider-verse-sets-animation-record-marvel/), [Axios](https://www.axios.com/2023/06/01/spiderman-across-the-universe-animation-latino)).
- **Pace and cost.** A widely reported figure, source not checked here: animators usually complete about four seconds of footage a week, but on the first film about one. Reporting in 2023 described repeated late revisions and heavy crunch on the sequel ([No Film School](https://nofilmschool.com/artists-working-conditions-spider-verse), [The Escapist](https://www.escapistmagazine.com/spider-man-across-the-spider-verse-production-work-rework-animators-arduous-phil-lord/)).

## Design from character, not style

Thompson designs from character: each visual choice should express who someone is and what they feel ([Cartoon Brew](https://www.cartoonbrew.com/feature-film/spider-man-into-the-spider-verse-production-design-is-about-character-not-style-168137.html)). The directors describe letting the story dictate the art, and say the sequel's turns in the story justified its many techniques ([AWN](https://www.awn.com/animationworld/fine-tuning-spider-verse-chat-justin-k-thompson), [DiscussingFilm](https://discussingfilm.net/2023/05/31/spider-man-across-the-spider-verse-directors-talk-raising-the-bar-and-creating-spider-punk-exclusive-interview/)). Tools were modelled on specific comic artists: Rick Leonardi's line work for Miguel, Brian Stelfreeze's for Jessica Drew ([AWN](https://www.awn.com/animationworld/fine-tuning-spider-verse-chat-justin-k-thompson)).

## Make CG look hand-made

From [CG Spectrum](https://www.cgspectrum.com/blog/spider-man-into-the-spider-verse-how-they-got-that-mind-blowing-look) for the first film and [befores & afters](https://beforesandafters.com/2024/01/10/giving-spider-man-across-the-spider-verse-that-crucial-hand-made-quality/) for the sequel:

- **Timing.** Characters are mostly animated on twos, a new pose every other frame; hair and cloth simulations run on ones so they do not jump. Our [montage measurement](../../apps/stop-motion/projects/spider-verse-dinner-montage/README.md#measured-timing) is consistent with a similar split: images change on twos while the frame moves on every frame.
- **No motion blur.** Stepped, repeated images create an echo instead. Smear frames last one or two frames at most.
- **Print instead of lens effects.** Halftone dots define light and reflections; shadows become hatching lines that thicken and thin. There is no soft glow. Red fringing and colour misregistration stand in for camera effects.
- **Ink lines over 3D.** The first film trained a machine-learning model on artists' face lines; its prediction was a starting point that artists corrected. The sequel's Houdini line system, Kismet, extends lines to full bodies, vehicles and environments, redraws them as characters move and offsets them slightly from the geometry. Hand-drawn Blender keys were interpolated and combined with the procedural lines.
- **Tools serve artists.** Miller says the machine-learning line tool is not generative AI, and that there is none in *Beyond the Spider-Verse* ([TheWrap, 2024-06-02](https://www.thewrap.com/spider-man-beyond-the-spider-verse-no-ai-chris-miller/)).

## Give each world its own art

The sequel gives each universe its own rules ([Screen Rant overview](https://screenrant.com/spider-man-across-the-spider-verse-animation-styles/), [Variety](https://variety.com/2023/film/focus/spider-man-across-spider-verse-animation-style-1235667268/)).

- **Earth-65, Gwen's world:** a living watercolor that acts as a mood ring. Colours shift with Gwen's feelings, and whatever lies outside her attention dissolves into abstract washes. Its primaries are cyan, orange and violet instead of yellow, red and blue. The look draws on Robbi Rodriguez's covers, with their vertical paint striations, Jason Latour's writing and Rico Renzi's colours. Houdini generated brush curves that drove Rebelle, a 2D watercolor painting application, producing wet-on-wet washes and sketchy line work that differ in every shot ([Sony Pictures Animation](https://x.com/SpiderVerse/status/1727044559665004549), [Screen Rant](https://screenrant.com/spider-man-across-the-spider-verse-clip-gwen-stacy/), [IndieWire](https://www.indiewire.com/features/animation/spider-man-across-the-spider-verse-animated-worlds-interview-1234874269/)).
- **Hobie Brown, Spider-Punk:** punk zine collage, with parts of him moving at different frame rates ([DiscussingFilm](https://discussingfilm.net/2023/05/31/spider-man-across-the-spider-verse-directors-talk-raising-the-bar-and-creating-spider-punk-exclusive-interview/)).
- **Mumbattan:** Indian Indrajal comics. **Nueva York:** clean retro-futurism. **The Spot:** rough, unfinished-looking ink.
- **The Lego universe:** a short sequence by Preston Mutanga, a teenage Blender artist hired after his fan-made Lego trailer.

## What this suggests for our films

Assistant synthesis, not tested:

- Choose the emotional rule first, such as colour following a character's mood, then the look.
- Treat timing as a style control: hold images on twos and move the camera on ones. Hard swaps feel hand-made where interpolation feels smooth.
- Design the imperfections: offset lines, misregistration, halftone and paper texture rather than soft glow and blur.
- Use generated images the way the studio used its line model: a first pass for an artist to select and correct.

## Hear the filmmakers

Thompson and the directors:

- [Artists Alley: the production designer's secrets](https://www.youtube.com/watch?v=TGXEh-YEj40) (SYFY Wire, 2019): how the first film's look was built. The best place to start.
- [Drawn to the Moment](https://www.youtube.com/watch?v=bbPez80qn4U) (2024): Thompson and Dos Santos on the sequel's animation.
- [Q&A with Phil Lord and the three directors](https://www.youtube.com/watch?v=LJdQNDmnOMo) and an [Annecy interview](https://www.youtube.com/watch?v=RF0DHQ9bTAU) recorded before the sequel's release.
- [Next Best Picture podcast](https://podcasts.apple.com/us/podcast/interview-with-spider-man-across-the-spider-verse/id1087678387?i=1000645709142) (February 2024), audio only.
- Written interviews: [Pictoplasma](https://pictoplasma.com/interview/justin-thompson/), [Letterboxd Journal](https://letterboxd.com/journal/powers-dos-santos-thompson-across-the-spider-verse-interview/), [Animation Magazine](https://www.animationmagazine.net/2023/05/the-directors-of-spider-man-across-the-spider-verse-detail-the-making-of-a-magnificent-sequel/), [Sony Future Filmmaker Awards](https://www.sonyfuturefilmmakerawards.com/news/conversation-justin-k-thompson-director-spider-man-across-spider-verse).

Crew and technical breakdowns:

- [Imageworks' breakdown reel for the sequel](https://www.youtube.com/watch?v=-uGZ702cuwE): shots built up layer by layer.
- [Houdini Connect talk by Ian Farnsworth and Pav Grochola](https://vimeo.com/354722683) and [SideFX's project page](https://www.sidefx.com/community/spider-man-into-the-spider-verse/): the first film's effects and ink lines.
- [Corridor Crew's animators react](https://geektyrant.com/news/animators-react-to-and-discuss-fantasia-spirited-away-family-dog-and-into-the-spider-verse), with Eric Koenig discussing the first film.
- Books: *The Art of Spider-Man: Into the Spider-Verse* and *The Art of Spider-Man: Across the Spider-Verse*.
- To go further: search ArtStation for "Spider-Verse", YouTube for "Spider-Verse SIGGRAPH", and follow crew names on IMDb or Letterboxd.

## Related films and shorts

- *K-Pop Demon Hunters* (2025) and *The Mitchells vs. the Machines* (2021): Sony Pictures Animation with Imageworks.
- *Puss in Boots: The Last Wish* (2022) and *The Bad Guys* (2022): DreamWorks' painterly, stepped action.
- *Teenage Mutant Ninja Turtles: Mutant Mayhem* (2023): a teenage-sketchbook look.
- *Arcane* (2021–2024): 3D painted to look hand-painted.
- *Nimona* (2023) and *Klaus* (2019).
- [*The Spider Within: A Spider-Verse Story*](https://en.wikipedia.org/wiki/The_Spider_Within:_A_Spider-Verse_Story) (2023): a short set in the same world.
- Alberto Mielgo's *The Windshield Wiper*, and "The Witness" and "Jibaro" from *Love, Death & Robots*.
