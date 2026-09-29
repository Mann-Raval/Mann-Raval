# Make this profile yours

## Publish Mann's profile

1. Sign in to GitHub as **Mann-Raval** and create a **public** repository named **Mann-Raval**. If it already exists, back up its contents before adding these files.
2. Upload this folder's contents, including `README.md`, `assets`, `profile.json`, `scripts`, `docs`, and `.github`. Keep the folder structure. The default branch should be `main` for the included push trigger.
3. Visit **https://github.com/Mann-Raval**. GitHub displays the root README automatically.
4. In the repository's **Actions** tab, enable workflows if prompted. Select **Refresh profile → Run workflow**. It also runs daily and when its source files change on `main`. The first successful run replaces the snake setup panels with animated light and dark contribution graphs for your account.

The active photo is `assets/mann_sunglasses.jpeg`, copied unchanged from the supplied portrait. Publishing the assets makes the included photos public.

GitHub's requirements: [Managing your profile README](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme).

## Reuse as a template

In the GitHub repository's Settings, enable **Template repository**. Others can select **Use this template** and name their new public repository after their own username.

1. Edit `profile.json`: replace the username, name, headline, bio, links, `stack_groups`, and projects. Badge entries contain a label, Simple Icons logo slug, and hex color. Project links use the configured username as owner.
2. Replace the photo specified in `profile.json` with your own portrait. Install Pillow with `python -m pip install Pillow`, then run `python scripts/prepare_portrait.py` to rebuild `assets/portrait.txt`. Adjust `portrait_crop` (left, top, right, bottom as fractions from 0 to 1) for another photo. To omit the portrait, set `photo` to an empty string and remove Mann's photos and `assets/portrait.txt` from your copy.
3. Update the three introduction bullets and closing invitation in `scripts/build_profile.py` if your focus differs. These are editorial text, not inferred GitHub data.
4. Run `python scripts/build_profile.py --fetch` with Python 3.12 or newer, or run the GitHub workflow. No packages need installing.
5. Review `README.md` with your editor's Markdown preview and commit the generated files.

For offline edits, run `python scripts/build_profile.py`. It reuses the saved stats for the same username. A changed username gets a neutral panel until refreshed, never the previous person's numbers.

## Design and data

- The main `assets/terminal.svg` matches the recording's composition: name header, green ASCII portrait on the left, profile details on the right, and a language bar below. Its eight-second loop reveals the portrait top to bottom, holds the completed portrait, then resets; the terminal cursor blinks every second. Reduced-motion viewers see the complete portrait. Animation is self-contained CSS inside SVG, with no JavaScript or external font required.
- `assets/portrait.txt` is a dense 144 × 112 character grid. `assets/portrait-tones.json` preserves brightness per character so the face retains its shadows and highlights. The sampler excludes the flat background using `portrait_background` (an RGB color; omit it for photos without a flat background). The original photo is unchanged. Daily builds use these checked-in files and do not require Pillow; Pillow is needed only when preparing a new portrait. Commit both files after preparing a new photo.
- Colorful logo badges use Shields.io and require that external service. The categories reflect the technologies in Mann's projects; unrelated Web3 and cybersecurity tools from the reference were not added.
- The contribution snake uses [Platane/snk](https://github.com/Platane/snk), runs daily, and writes both light and dark SVGs into `assets`. GitHub automatically selects the matching theme. It represents the contribution calendar, not just commit counts. The checked-in setup panels are explicitly placeholders until the first GitHub Actions run; no contribution history has been invented.
- The README uses GitHub-compatible HTML and Markdown. Your photo remains a separate JPEG because GitHub does not reliably support linked raster images inside SVGs.
- Stats use GitHub's public REST API. Stars and primary-language counts exclude forks; public repository count includes them. Languages count repositories by their primary language, not bytes or proficiency. These are snapshots, not live counters or contribution totals.
- The workflow uses the automatic GitHub token. No personal access token is required. It does not access private repository contents.
- A failed API request fails the build before overwriting the profile. The previous committed images remain available.
- Branch protection or organization policy may block the bot's push. Review the workflow logs; generate locally and commit through your normal pull-request process if needed.
- Scheduled workflows can be delayed or disabled after repository inactivity. Run the workflow manually to refresh.
- Header text is designed for short names and taglines. Preview longer replacements and adjust font sizes in the generator if needed.

## Inspiration

Inspired by the introduction, toolbox, project, and stats sections of [MfrankUg](https://github.com/MfrankUg), [devdesai06](https://github.com/devdesai06), and the visual profile presentation of [Igorcbraz](https://github.com/Igorcbraz). The layout and artwork here are original.

Project descriptions were based on Mann's public repository metadata and READMEs. No job title, education, location, or unverified social account was added.
