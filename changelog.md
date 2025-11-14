# changelog

## 14/11/25
Reworked most parts. Still not useful but the changelog gen is much improved.

## 13/11/25
Rough week. Haven't gotten too much done lately but am still working on it.

## 9/11/25
Diffed the json dumps, but now I'm neck deep in blender sourcecode again and I might have found a third way. A lovely combination of the two - the relatively minimal, clean aspects of the HTML visually, without the mess of it behind the scenes, but readible in a way the html formatting isn't - .\doc\python_api\rst\change_log.rst

The primary issue remains the actual parsing of the text. Looking into AST extractors etc. Well outside my wheelhouse, but that's how you learn, right?
 -- harpoon

## 8/11/25
The JSON dump getter/cleaner is updated with args and version selection. Provided source + target versions, it'll get+clean those api dumps.
Really this feels very home-baked; it feels like it should be a remote resource. But this wil do for now. idk, I like the idea of just downloading+cleaning them once and then carrying on from there. But will see. If I can get it working at all it'll be a miracle, so I'm not too worried about the theoretical ideal just yet.
 -- harpoon

## 7/11/25

So I just found api_dump_index.json.

Each API has a full json dump.
Why am I trying to parse HTML changelogs if there are json dumps?

Haven't looked into it too much yet but oh this is lovely. I'm sure https://docs.blender.org/api/2.92/api_dump.json isn't meant to be reading material but I love it.

-- harpoon

