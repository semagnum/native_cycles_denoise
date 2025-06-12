# Native Cycles (Temporal) Denoise

Did you know that Cycles has built-in (but limited) support for temporal denoising?
You're not alone.
Unless you check the
[release notes of 3.1](https://developer.blender.org/docs/release_notes/3.1/cycles/#features),
this [stackexchange post](https://blender.stackexchange.com/questions/181921/how-to-denoise-animations-using-blenders-temporal-denoiser),
or the Cycles source code, you wouldn't know either.

It is already available via Blender's Python API,
but not the UI.
This add-on adds two operators to the render menu
to give you easy access to these features:

- render an animation, then immediately denoise it
- denoise an existing multilayer EXR image sequence at your scene's output path

## Requirements

- Blender 3.1 or later
- Cycles
- you must enable "Vector" and "Denoising Data" render passes
- your export format must be multilayer EXR (to save all the passes)

You may need an Optix-supported render device for this to work,
but I haven't been able to confirm that yet since I do have one.
If you don't, please let me know if it works.


Shoutout to Jonathan Lampel for telling me where it is.