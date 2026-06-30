from ascii_magic import AsciiArt

art = AsciiArt.from_image("assets/splash.png")

ascii_text = art.to_ascii(columns=140)

with open("assets/splash.txt", "w", encoding="utf-8") as f:
    f.write(ascii_text)

print("Готово: assets/splash.txt")
