Conceptually, a converter between different forms of Blender Python  API. There are hard limits of course, where function has changed far beyond simple API calls, but for renames, same-intent 1:1 calls, this feels doable. And for the parts that aren't doable for conversion, at least being able to mark what's not working and why - no more spending an hour trying to fix node sockets only to realise it's failing because the tutorial used last year's socket-creation command. (Not that I've done that myself at all, of course. Some... conceptual person might have, though. Poor dear.)

As of 11:25: Started yesterday afternoon. So far it's just the HTML parser, but it does read both the 2.78 and 4.0 API changelog, so hopefully the parts in the middle won't be too much more difficulty to parse. Once the parser's done, I can start on the script analysis part. Should look into linters, seems relevant. 

-- harpoon
