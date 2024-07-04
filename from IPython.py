
from IPython.display import Markdown, display
import textwrap

def to_markdown(text: str) -> str:
  if not isinstance(text, str):
        raise TypeError("Input must be a string")
  text = text.replace("•", " ✶")
  return Markdown(textwrap.indent(text, '> ', predicate = lambda _:True))

text = """
* **Sunlight is made up of all colors of the rainbow.**  These colors have different wavelengths, with blue light having a shorter wavelength than red light.
* **When sunlight enters the Earth's atmosphere, it interacts with tiny particles like nitrogen and oxygen molecules.** These 
particles are much smaller than the wavelength of visible light.
* **These particles scatter the sunlight in all directions.** However, they scatter blue light much more strongly than other colors because of its shorter wavelength.
rter wavelength than red light.
* **When sunlight enters the Earth's atmosphere, it interacts with tiny particles like nitrogen and oxygen molecules.** These 
particles are much smaller than the wavelength of visible light.
* **These particles scatter the sunlight in all directions.** However, they scatter blue light much more strongly than other colors because of its shorter wavelength.
* **This scattered blue light reaches our eyes from all directions, making the sky appear blue.**

* **When sunlight enters the Earth's atmosphere, it interacts with tiny particles like nitrogen and oxygen molecules.** These 
particles are much smaller than the wavelength of visible light.
* **These particles scatter the sunlight in all directions.** However, they scatter blue light much more strongly than other colors because of its shorter wavelength.
* **This scattered blue light reaches our eyes from all directions, making the sky appear blue.**

This scattering effect is more pronounced when the sun is low on the horizon (like at sunrise or sunset), which is why the skyparticles are much smaller than the wavelength of visible light.
* **These particles scatter the sunlight in all directions.** However, they scatter blue light much more strongly than other colors because of its shorter wavelength.
* **This scattered blue light reaches our eyes from all directions, making the sky appear blue.**

This scattering effect is more pronounced when the sun is low on the horizon (like at sunrise or sunset), which is why the sky* **This scattered blue light reaches our eyes from all directions, making the sky appear blue.**
"""

Markdown(text)


print("Gay")
