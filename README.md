# Nekoro Gear

Crystals, metals, tools, armor and building blocks in 40 colours, the base of my other Nekoro mods.

Made for my [Nekoro Pokemon](https://www.curseforge.com/minecraft/modpacks/nekoropolia) modpack, but it works with any mods. Required on the client and the server.

## Features

- **Materials:** 24 crystals, 5 metals and 2 alloys with ores, plus gear for vanilla materials without it.
- **Tools and armor:** the vanilla set for every material; the stats of every item are set in `config/Nekoro/Gear/items.json`.
- **Building blocks:** bricks, small bricks, smooth blocks with stairs and slabs, pillars and lamps in all 40 colours.
- **Ores:** spread like vanilla ores; the amount in the deepslate and stone layers is set in `config/Nekoro/Gear/options.json`.

## Building

Needs JDK 21. `source/tools/generate.py` writes the textures, models and data from the material list;
`source/build-all.ps1` builds NeoForge and Fabric for Minecraft 1.21.1 into `release/<version>`.

## License

MIT, see [LICENSE](LICENSE).
