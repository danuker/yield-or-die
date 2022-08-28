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

- [Installation](#installation)
- [Feature wishlist](#feature-wishlist)

![Screenshot](pics/screenshot.png)

# Development

You need Kivy, Buildozer, and JDK.

- Install OS dependencies first
    - For Arch Linux these are: `sudo pacman -Sy android-tools sdl2 sdl2_image sdl2_mixer sdl2_ttf`

- Then Python dependencies; rebuilds Kivy because of audio bug in Pip binary
    - `pip install -r requirements.txt`

After you install the dependencies, you can run using:

`python main.py`

But the project is more fun on (and designed for) a mobile phone. Read further.

# Android

## You need JDK

Android requires JDK and Gradle.

On Arch Linux, you can try:
    sudo pacman -Sy jdk-openjdk gradle


## Deploy on Android

To deploy on Android, you need `adb` and other tools in the Android SDK.

After changing `buildozer.spec` or your Java installation, you probably need to run:

    buildozer appclean

To show devices:

    adb devices

Check that the device is visible (search for the error if you do not see similar output):

    List of devices attached
    6b7fa94 device

Finally, deploy to the device:

    buildozer android debug deploy run

This will take a while the first time; Buildozer has a lot of dependencies,
including the Android SDK for which there are two (??) license agreements.

On my 6-year-old laptop it took 30 minutes.

Compilation will use CPU; make sure you have adequate cooling and/or thermal throttling.

A built APK file will be available in `yield-or-die/.buildozer/android/platform/build-armeabi-v7a/dists/yield_or_die/build/outputs/apk/debug/`.

## Regenerating images

If you edit the graphics, you need to generate PNGs from the SVGs,
because Kivy does not support SVG, but SVG has superior editability for the style.

This requires commands from the `imagemagick` package: `mogrify` and `convert`.
To perform it:

    cd pics/
    ./generate_pngs.sh
    

Because the vast majority of people will not edit the graphics,
the PNGs are in the Git repo as well (whole project is under 3MB anyway).

Alternatively you can edit the PNGs directly.

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
        - `>=100`: "You are a traffic god!", "This humble game bows before you.", "You have achieved mastery.", "You have learnt everything this game can teach you."
        - `>=50`: "Well played!", "You had a good run. Can you do it again?", "You played okay, and postponed certain death.", "You might not die in traffic! But keep practicing."
        - `>=30`: "You need more practice." "There is hope for you.", "You are improving!", "Keep at it!"
        - `>=10`: "Sign up for organ donation!", "I'm thinking of reporting you to the police.", "You need much more patience!", "2.6% of deaths occur in traffic accidents. You might be one of them!"
        - `>=5`: "This is ridiculous.", "You won't last long on the streets.", "Are you a kid? You're not allowed to drive!"
        - `>=0`: "Tap to try again!" (don't scare off newbies)
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

