import json
import subprocess


def choose_camera() -> int:
    script = '''
import AVFoundation
import Foundation
let names = AVCaptureDevice.devices(for: .video).map { $0.localizedName }
let data = try JSONSerialization.data(withJSONObject: names)
print(String(data: data, encoding: .utf8)!)
'''
    try:
        result = subprocess.run(
            ["/usr/bin/swift", "-e", script], capture_output=True, text=True,
            check=True, timeout=30,
        )
        names = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        raise RuntimeError(
            "Cannot list camera names safely. Check that Apple's Swift tools are available; "
            "alternatively pass --camera INDEX for a known physical camera."
        ) from error
    if names == []:
        raise RuntimeError("No video cameras found. Check camera connections and permissions.")
    cameras = {
        index: name for index, name in enumerate(names)
        if "obs virtual camera" not in name.casefold()
    }
    if not cameras:
        raise RuntimeError("No selectable cameras found. OBS Virtual Camera is output-only.")
    print("\nAvailable cameras:")
    for index, name in cameras.items():
        print(f"  {index}: {name}")
    while True:
        try:
            answer = input("Camera number (or q to cancel): ").strip()
        except EOFError as error:
            raise RuntimeError("Camera selection needs a terminal; alternatively pass --camera INDEX.") from error
        if answer.lower() == "q":
            raise SystemExit(0)
        if answer.isascii() and answer.isdecimal():
            index = int(answer)
            if index in cameras:
                print(f"Using camera {index}: {cameras[index]}")
                return index
        print("Enter one of the listed camera numbers.")