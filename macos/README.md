# VanishCam for macOS and Microsoft Teams

Gesture-controlled webcam effects for Microsoft Teams on Mac: a dissolve,
a Naruto-style smoke-and-log substitution, and animated Goku-style teleportation.
Video is processed locally and sent to Teams through the OBS Virtual Camera driver.

This is a macOS launcher and teleport extension for
[Nicovic17/vanish_webcam](https://github.com/Nicovic17/vanish_webcam), not an
official Dragon Ball, Naruto, Microsoft, or OBS product.

## Requirements

- An Apple Silicon Mac with a webcam. Tested on an M4 Max running macOS 15.7.5;
  Intel Macs and other macOS releases have not been verified.
- Microsoft Teams desktop app.
- [Homebrew](https://brew.sh/), Git, and `uv` for installation.
- OBS Studio 30 or newer, installed specifically at `/Applications/OBS.app`.
- Internet access for the initial dependencies and MediaPipe model downloads.
- Permission to use the webcam and enable the OBS camera extension. Managed Macs
  may require IT approval; this setup does not bypass company policies.

## Install on Mac

### 1. Install the prerequisites

Run these commands in Terminal after installing Homebrew:

```bash
brew install git uv
brew install --cask --appdir=/Applications obs
```

If OBS is already installed, verify that it is in `/Applications`, not
`~/Applications`. OBS cannot install its camera extension from the latter location.
Enter any administrator password directly into your local installation prompt.

### 2. Get this fork

```bash
git clone https://github.com/frsnjung/vanish_webcam.git
cd vanish_webcam/macos
```

Run all remaining commands from `macos/`, where this README, `launch.sh`,
`teleport.py`, and `requirements-macos.txt` live. The launchers use the existing
source files in the repository root; no additional upstream checkout is needed.
If you download a ZIP instead, extract it and open Terminal in its `macos/` folder.

### 3. Create the isolated Python environment

Run from the project folder:

```bash
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-macos.txt
chmod +x launch.sh *.command
./launch.sh --check
```

The health check downloads missing segmentation/gesture models and initializes the
Normal and Naruto models without opening the webcam. Python and dependencies live
in `.venv`; no changes to another project's environment are needed.

Use the Mac-specific dependency file, not upstream's requirements. The tested
versions are MediaPipe 0.10.20, OpenCV 4.11.0.86, NumPy 1.26.4,
pyvirtualcam 0.15.0, and pygame 2.6.1. Newer upstream combinations crashed during
model initialization on the test Mac.

### 4. Add your teleport sound

The current teleport launcher requires `teleport.wav` in the `macos/` folder.
Supply a sound you have permission to use; it is not downloaded automatically.
For an M4A clip, replace the example input path below with your file:

```bash
afconvert -f WAVE -d LEI16 "$HOME/Downloads/your-teleport-sound.m4a" teleport.wav
./.venv/bin/python teleport.py --self-test
```

macOS includes `afconvert`. The original file is not modified and is not needed
after conversion. A short clip of roughly one second works well. The self-test
decodes the audio and checks face, hand, segmentation, and animation processing;
it does not play the clip or open the webcam.

### 5. Enable the OBS camera extension

1. Open OBS Studio from Applications. Skip its auto-configuration wizard if offered.
2. Click **Start Virtual Camera** in OBS's Controls area.
3. If prompted, approve the extension in **System Settings > General > Login Items
   & Extensions > Camera Extensions**. Enable OBS and restart OBS if requested.
   Settings labels can vary by macOS version.
4. Confirm the virtual camera can start, then click **Stop Virtual Camera**.
5. Quit OBS with **Cmd+Q**.

No OBS scene, screen capture, or screen sharing is needed. VanishCam sends frames
directly through the installed OBS driver. **OBS's own virtual-camera output must
remain stopped while VanishCam is running.**

### 6. Allow webcam access

Double-click **Preview Only.command** in Finder and allow Terminal to access the
camera. If access is denied, enable Terminal under **System Settings > Privacy &
Security > Camera**, quit the launcher, and start it again. If launched through a
different host app, macOS may request camera access for that app instead.

Step out of view for four seconds, return, and try the Normal-mode V gesture.
Click the preview and press **R** to return or **Q** to quit.

## Use in Microsoft Teams

1. Close any running VanishCam instance and keep OBS closed.
2. Double-click one of the effect launchers listed below.
3. Leave the camera's field of view for the first **four seconds** while the empty
   background is captured. Wait for the terminal's background-ready message.
4. In Teams, open **Settings > Devices > Camera**, or the meeting camera settings,
   and select **OBS Virtual Camera**.
5. Turn off Teams background blur, replacement backgrounds, and other video effects.
6. Return to your seat and perform the gesture. Teams participants receive the
   processed video, including the disappearance and animation.

If OBS Virtual Camera does not appear, fully quit and reopen Teams after enabling
the OBS extension. If Teams keeps showing an old image, switch to another camera
and back to OBS Virtual Camera after starting VanishCam.

Keep the camera, lighting, and background still. Moving objects or changing light
can reveal the difference between the captured background and the live frame.
Teams may mirror your own preview; the outgoing VanishCam image is not mirrored.

## Effects and controls

| Launcher | Trigger | Effect | Return |
| --- | --- | --- | --- |
| **Start VanishCam.command** | Index and middle fingers in a V | Gradual dissolve | **R** in preview |
| **Start Naruto.command** | Bring both palms together | Smoke and substitution log | **R** in preview |
| **Start Teleport.command** | Two straight fingers together at forehead for one second | Animated vertical streaks and a sharp teleport | Lower hand, then repeat gesture |
| **Preview Only.command** | Same as Normal | Local preview without virtual output | **R** in preview |

For teleportation, fold the other fingers and keep your face and hand visible to
the physical webcam. Lower your hand for at least half a second before repeating
the one-second pose. Tracking continues while the output shows you as invisible.
The 0.65-second animation reverses on return; your sound plays in both directions.

Keyboard controls require the **preview window to have focus**:

| Key | Action |
| --- | --- |
| **R** | Immediately return to live video |
| **Space** | Recapture the empty background; step out again for four seconds |
| **V** | Manually trigger Normal or Naruto; not supported in teleport mode |
| **Q / Escape** | Quit and release the camera |

Run only one launcher at a time. To stop using the effect, quit VanishCam and select
your physical webcam in Teams.

## Audio and privacy

Sound plays through the Mac's selected audio output. **OBS Virtual Camera carries
video only; sound is not injected into the Teams microphone.** Your normal Teams
microphone selection stays unchanged. Direct sound transmission would need a
separate virtual-audio setup; this project does not configure one.

Webcam processing is local. The app adds no video recording, cloud inference, or
startup service. Teams transmits the selected camera feed normally. Installation
downloads packages and models; terminal diagnostics are saved locally under `logs/`.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| OBS Virtual Camera missing | OBS must be in `/Applications`; approve its camera extension and restart Teams. |
| Camera unavailable or permission denied | Enable camera access for Terminal, restart the launcher, and close competing camera apps. |
| Effect appears locally but not in Teams | Select OBS Virtual Camera, disable Teams effects, and switch cameras away and back. Stop OBS's own output. |
| Virtual-camera output cannot start | Quit OBS and other VanishCam instances, then restart one launcher. |
| Gesture does not trigger | Improve lighting, show the full hand and face, and hold the pose steadily. Teleport fingers must be together, not a V. |
| Background looks wrong | Keep the camera still; press Space and leave the picture during recalibration. |
| Teleport reports missing audio | Create `teleport.wav` in `macos/` using the conversion step above. |
| Other participants cannot hear the sound | Expected: audio is local, not routed through OBS Virtual Camera. |

For Normal/Naruto with multiple webcams, run `./launch.sh --camera 1` or
`./launch.sh --mode naruto --camera 1`. Teleport currently uses camera index 0.

Diagnostics: `logs/latest.log` for Normal/Naruto/preview and `logs/teleport.log` for
teleport. Model checks: `./launch.sh --check` and
`./.venv/bin/python teleport.py --self-test`. Some older MediaPipe wheels report an
x86-only internal wheel tag despite working natively on the test Apple Silicon
Mac; model inference is a more useful health check than `pip check` alone.

## Development checks

From the project folder, without opening a webcam:

```bash
./.venv/bin/python -m unittest test_teleport test_teleport_effect -v
./.venv/bin/python teleport.py --self-test
bash -n launch.sh "Start Teleport.command"
```

The local suite covers gesture timing, release-to-rearm, animation endpoints,
moving streaks, reversed return, and distant-background preservation. Live webcam
tracking and Teams output still require a manual check. The pinned upstream suite
has two known failures in gesture retry/crop expectations, separate from these tests.

## Publishing checklist

The Mac launchers, Python extensions/tests, dependency pins, and this README live
under `macos/`. Its ignore rules exclude `.venv/`, `__pycache__/`, `logs/`,
`.DS_Store`, and `teleport.wav`. Do not upload personal downloads or recordings.

This fork retains upstream source and history at the repository root. The upstream
revision used here has no root LICENSE file; verify permission and applicable
terms before further redistribution of its code or bundled assets. Attribution
alone does not establish redistribution rights.

Do not publish `teleport.wav` unless you have redistribution rights to the clip.
The setup supports users supplying their own audio. Choose a license for your own
contributions separately and do not imply it covers third-party code or assets.

## Credits and compatibility

Normal and Naruto processing comes from
[Nicovic17/vanish_webcam](https://github.com/Nicovic17/vanish_webcam), pinned to
`1e008cf3fb19a9c9a63dc690e81b46ccacab8475`. That revision's README advertises Goku
mode and `assets/teleport.MP3`, but neither implementation nor audio asset is
present in its published source. The local `teleport.py` and `teleport_effect.py`
provide this project's separate animated implementation using MediaPipe models.

Camera output uses [OBS Studio](https://obsproject.com/) and
[pyvirtualcam](https://github.com/letmaik/pyvirtualcam); tracking uses
[MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide).
Review each dependency's own license and model terms. Avoid updating upstream or
replacing the pinned Python dependencies without repeating the Mac health checks.