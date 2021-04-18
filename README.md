Yield or Die! Train yourself to learn rules for right-of-way, 
without spending lots of money for practice at driving school!

Disclaimer: learn at your own risk.

Copyright (C) 2021 Dan Gheorghe Haiduc (aka danuker)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

----

That said, the author personally used this software to efficiently practice,
and is now the proud owner of a driver's license (4th time was the charm).

The rules were written for Romania, but they are probably very similar 
for most of continental Europe.

I appreciate contributions, especially for inclusion in [F-Droid](https://f-droid.org/).


Contents:

- Installation
- Feature wishlist


# Installation

You need Kivy, Buildozer, and JDK 8.

- Install OS dependencies first
- For Arch Linux these are:
    - `sudo pacman -Syu sdl2 sdl2_image sdl2_mixer sdl2_ttf`

- Then Python dependencies; rebuilds Kivy because of audio bug in Pip binary
    - `pip install -r requirements.txt`

After you install the dependencies, you can run using:

`python main.py`

But the project is more fun on a mobile phone. Read further.

## You need JDK 8

Android requires JDK.

Since Oracle [changed its license](https://www.oracle.com/java/technologies/javase-jdk8-downloads.html)
for newer versions of `openjdk-8-jdk`,
I point anyone interested to an alternate implementation of JDK 8, which got me past an error:

[AdoptOpenJDK](https://adoptopenjdk.net/installation.html)


## Deploy on Android

To deploy on Android, you need `adb` and other tools in the Android SDK.

When opening a new console, before doing any Buildozer commands, you need AdoptOpenJDK in the path:
    export PATH=$PWD/jdk8u242-b08/bin:$PATH

After changing buildozer.spec, you might need to run:
    buildozer appclean

To deploy and run on a device:
    adb devices     # check that device is visible
    buildozer android debug deploy run


## Regenerating images

If you edit the graphics, you need to generate PNGs from the SVGs,
because Kivy does not support SVG, and SVG has superior editability.

This requires commands from the `imagemagick` package: `mogrify` and `convert`.
To perform it:

    cd pics/
    ./generate_pngs.sh
    

Because the vast majority of people will not edit the graphics,
the PNGs are in the Git repo as well (whole project is under 2MB anyway).


# Feature wishlist

Report statistics:

- all time intersections, and won %
- last 100 intersections won %
- last 1000 won% ?
- Top score: consecutive correct

Features:

- DO NOT timeout if no move made
    - too short timeout encourages risky behaviour
    - I failed my 3rd exam because of this
    - still, the cars should animate somehow as approaching the intersection
        - perhaps slow to a halt?
- persistent side of road config option
    - needs menu?
- persistent high score record, also display it at end (compared to current score)
    - allow input of player name
- don't freeze cars if player only tapped screen, only show hint
- country localized signs; check regional rules

- losing screen: score, high score
    - store score to HDD
    - fireworks if beaten or matched high score
    - explain mistake ("had RoW but did not go in 20s" or "other car had RoW")
    - share button

- effects
    - animation:
        - before player moves: vehicles go slowly, constantly
        - after player moves: go faster; crash if needed
    - audio (freesound - test with all speakers and headphones):
        1. sounds of explosion/crash
        2. engine at various RPM ~ speed, tweak pitch and volume
        3. fireworks
    - text:
        - funny messages:
        - >=100: "You are a traffic god!", "This humble game bows before you.", "You have achieved mastery.", "You have learnt everything this game can teach you."
        - >=50: "Well played!", "You had a good run. Can you do it again?", "You played okay, and postponed certain death.", "You might not die in traffic! But keep practicing."
        - >=30: "You need more practice." "There is hope for you.", "You are improving!", "Keep at it!"
        - >=10: "Sign up for organ donation!", "I'm thinking of reporting you to the police.", "You need much more patience!", "2.6% of deaths occur in traffic accidents. You might be one of them!"
        - >=5: "This is ridiculous.", "You won't last long on the streets.", "Are you a kid? You're not allowed to drive!"
        - >=0: "Tap to try again!"
    - animations:
        - vehicles keep going until crashing or cleared
    - visual:
        1. explosion if crashing
        2. smooth turning instead of 90 degree instantly
        3. fireworks after beating record
        4. player's car different
        5. better car, road gfx (pixel art?)
        6. crumpled & darkened cars after crash

- other vehs moving along their path, so that they intersect at same time
    - they also accelerate if you accelerate
    - but stop when they must yield, and you win the turn

- landscape mode? min of width and height -> lane_width

