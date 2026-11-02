# 💗 Neural Bloom // 089 — Setup Guide

## 1. Publish your profile

1. Make sure your repository is **public**.
2. The repository name must be exactly `Deekshitha-089`.
3. Place `README.md` at the root of the repository.
4. Keep the `assets` folder and `.github` folder in the repository.
5. Commit and push your changes to the `main` branch.

Your profile README will appear on your GitHub profile page.

## 2. Neon pink contribution heatmap

The README uses the following external service to display your GitHub contribution activity in neon pink:

`https://ghchart.rshah.org/FF4FC3/Deekshitha-089`

The heatmap reflects your actual GitHub contributions.

If the image does not load, the external service may be temporarily unavailable.

## 3. Generate the pink contribution snake

The repository includes a GitHub Actions workflow that generates a pink contribution snake.

### Enable workflow permissions

1. Open your repository on GitHub.
2. Go to **Settings → Actions → General**.
3. Scroll down to **Workflow permissions**.
4. Select **Read and write permissions**.
5. Click **Save**.

### Run the workflow

1. Open the **Actions** tab.
2. Select **Generate pink contribution snake**.
3. Click **Run workflow**.
4. Select the `main` branch.
5. Click **Run workflow** again.

Wait for the workflow to finish successfully.

The generated snake will be published to the `output` branch.

## 4. Troubleshooting

### The snake is not appearing

- Check that the workflow completed successfully.
- Make sure workflow permissions allow read and write access.
- Confirm that the `output` branch exists.
- Refresh your profile README after the workflow completes.

### The pink heatmap is not appearing

The heatmap is provided by an external image service. If the service is unavailable, the image may not load.

### The profile README is not appearing

Confirm that:

- The repository is public.
- The repository name matches your GitHub username exactly.
- `README.md` is located at the repository root.

---

<div align="center">

Made with 💗 and curiosity.

</div>