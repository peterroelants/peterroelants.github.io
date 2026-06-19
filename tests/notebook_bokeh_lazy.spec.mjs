import { expect, test } from "@playwright/test";

test("MENACE Bokeh output loads lazily and remains interactive", async ({
  page,
}) => {
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.goto("/posts/post_03_delayed_feedback_menace/");
  const output = page.locator("[data-bokeh-script]").first();

  await expect(output).toHaveCount(1);
  await expect(page.locator('script[src*="/js/bokeh/3.9.1/"]')).toHaveCount(0);
  await expect(output.locator("canvas")).toHaveCount(0);

  await output.scrollIntoViewIfNeeded();
  await expect(output.locator("canvas")).toHaveCount(2, { timeout: 15_000 });
  await expect(
    page.getByRole("button", { name: "Sample MENACE move" })
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Reset game" })).toBeVisible();

  const sampleButton = page.getByRole("button", { name: "Sample MENACE move" });
  await expect(sampleButton).toBeEnabled();
  await sampleButton.click();
  await expect(page.getByText("Your turn.", { exact: false })).toBeVisible({
    timeout: 5_000,
  });
  await expect(
    page.getByRole("button", { name: "Click board to play your move" })
  ).toBeDisabled();
  expect(pageErrors).toEqual([]);
});

test("all tagged Bokeh posts load their standalone outputs lazily", async ({
  page,
}) => {
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  const cases = [
    {
      path: "/posts/beta-distribution-probabilities/",
      minimumCanvases: [1, 1, 1],
      controls: "Add success",
    },
    {
      path: "/posts/beta-prior-sequential-binary-decisions/",
      minimumCanvases: [2],
      controls: "Run",
    },
    {
      path: "/posts/gaussian-process-kernel-fitting/",
      minimumCanvases: [1, 1, 1],
    },
  ];

  for (const testCase of cases) {
    await page.goto(testCase.path);
    const outputs = page.locator("[data-bokeh-script]");
    await expect(outputs).toHaveCount(testCase.minimumCanvases.length);
    await expect(
      page.locator("script").filter({ hasText: "embed_items" })
    ).toHaveCount(0);

    for (let index = 0; index < testCase.minimumCanvases.length; index += 1) {
      const output = outputs.nth(index);
      await output.scrollIntoViewIfNeeded();
      await expect
        .poll(() => output.locator("canvas").count(), { timeout: 15_000 })
        .toBeGreaterThanOrEqual(testCase.minimumCanvases[index]);
    }

    if (testCase.controls) {
      await expect(
        page.getByRole("button", { name: testCase.controls })
      ).toBeVisible();
    }
  }

  expect(pageErrors).toEqual([]);
});

test("lazy loader waits for an existing script that is still loading", async ({
  page,
  baseURL,
}) => {
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.route("**/delayed-bokeh.js", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 150));
    await route.fulfill({
      contentType: "application/javascript",
      body: "window.delayedBokehReady = true;",
    });
  });
  await page.route("**/delayed-app.js", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: `
        if (!window.delayedBokehReady) {
          throw new Error("The Bokeh bundle was not ready before the app ran");
        }
        document.querySelector("[data-bokeh-script]").dataset.appLoaded = "true";
      `,
    });
  });

  await page.goto("/");
  await page.setContent(
    `
      <base href="${baseURL}/">
      <script>
        window.IntersectionObserver = undefined;
        const delayed = document.createElement("script");
        delayed.src = "/delayed-bokeh.js";
        document.head.appendChild(delayed);
      </script>
      <div data-bokeh-script="/delayed-app.js"
           data-bokeh-bundles='["/delayed-bokeh.js"]'>
        <p class="notebook-bokeh-lazy-status">Loading</p>
      </div>
      <script src="/js/notebook_bokeh_lazy.js"></script>
    `,
    { waitUntil: "domcontentloaded" }
  );

  await expect(page.locator("[data-app-loaded]"))
    .toHaveAttribute("data-app-loaded", "true", { timeout: 5_000 });
  expect(pageErrors).toEqual([]);
});
