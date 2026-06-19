/*
 * Notebook conversion turns selected standalone Bokeh outputs into static
 * assets. This loader keeps those assets out of the initial page load and
 * starts them only when a visitor is likely to view the output. The published
 * page remains a static site: BokehJS and the generated embed script run in
 * the visitor's browser, with no Python process or Bokeh server involved.
 */
(function () {
  "use strict";

  // Several outputs can share the same BokehJS bundle. Cache promises so a
  // bundle is requested once and every dependent output waits for that load.
  var loadedScripts = new Map();

  function loadScript(src) {
    if (typeof src !== "string" || !src) {
      return Promise.reject(new Error("Cannot load an empty script URL"));
    }
    if (loadedScripts.has(src)) {
      return loadedScripts.get(src);
    }

    var promise = new Promise(function (resolve, reject) {
      var absoluteSrc;
      try {
        absoluteSrc = new URL(src, document.baseURI).href;
      } catch (error) {
        reject(new Error("Invalid script URL: " + src));
        return;
      }

      var existing = Array.from(document.scripts).find(function (script) {
        return script.src === absoluteSrc;
      });

      var created = !existing;
      var script = existing || document.createElement("script");
      if (created) {
        script.src = src;
        // Bundle order is controlled by the promise chain below. Keeping
        // dynamic scripts non-async also makes that dependency explicit.
        script.async = false;
      }

      var settled = false;
      function cleanup() {
        script.removeEventListener("load", resolveOnce);
        script.removeEventListener("error", rejectOnce);
      }
      function resolveOnce() {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        script.dataset.notebookBokehLoaded = "true";
        resolve();
      }
      function rejectOnce() {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        reject(new Error("Could not load " + src));
      }

      // Listen before appending a new script, and also handle a script that
      // another loader has already inserted but is still in flight.
      script.addEventListener("load", resolveOnce);
      script.addEventListener("error", rejectOnce);
      if (
        script.dataset.notebookBokehLoaded === "true" ||
        script.readyState === "loaded" ||
        script.readyState === "complete"
      ) {
        resolveOnce();
      } else if (created) {
        document.head.appendChild(script);
      }
    });
    loadedScripts.set(src, promise);
    return promise;
  }

  // The converter controls these attributes. The caller validates them before
  // starting the chain so malformed generated HTML fails visibly instead of
  // producing an uncaught asynchronous error.
  function loadBokehBundles(bundles) {
    return bundles.reduce(function (promise, src) {
      return promise.then(function () {
        return loadScript(src);
      });
    }, Promise.resolve());
  }

  function failOutput(container) {
    container.dataset.bokehLoaded = "error";
    container.setAttribute("aria-busy", "false");
    var status = container.querySelector(".notebook-bokeh-lazy-status");
    if (status) {
      status.textContent = "Interactive visualization could not be loaded.";
    }
  }

  function prepareContainer(container) {
    container.setAttribute("role", "region");
    container.setAttribute(
      "aria-label",
      container.dataset.bokehTitle || "Interactive Bokeh visualization"
    );
    container.setAttribute("aria-busy", "true");
  }

  function loadBokehOutput(container) {
    if (
      container.dataset.bokehLoaded === "true" ||
      container.dataset.bokehLoaded === "loading" ||
      container.dataset.bokehLoaded === "error"
    ) {
      return;
    }
    container.dataset.bokehLoaded = "loading";

    var scriptSrc = container.dataset.bokehScript;
    var bundles;
    try {
      bundles = JSON.parse(container.dataset.bokehBundles || "[]");
    } catch (error) {
      console.error("Invalid lazy Bokeh bundle list", error);
      failOutput(container);
      return;
    }

    if (
      !scriptSrc ||
      !Array.isArray(bundles) ||
      !bundles.length ||
      bundles.some(function (src) {
        return typeof src !== "string" || !src;
      })
    ) {
      console.error("Lazy Bokeh output is missing its script or bundles");
      failOutput(container);
      return;
    }

    loadBokehBundles(bundles)
      .then(function () {
        return loadScript(scriptSrc);
      })
      .then(function () {
        container.dataset.bokehLoaded = "true";
        container.setAttribute("aria-busy", "false");
        var status = container.querySelector(".notebook-bokeh-lazy-status");
        if (status) {
          status.remove();
        }
      })
      .catch(function (error) {
        console.error("Lazy Bokeh output failed", error);
        failOutput(container);
      });
  }

  function initialize() {
    var outputs = Array.from(document.querySelectorAll("[data-bokeh-script]"));
    if (!outputs.length) {
      return;
    }
    outputs.forEach(prepareContainer);

    if (typeof IntersectionObserver !== "function") {
      // Older browsers still get the interactive; they simply do not get the
      // deferred network request that IntersectionObserver enables.
      outputs.forEach(loadBokehOutput);
      return;
    }

    // Start loading slightly before an output enters the viewport so the
    // interaction is ready when the visitor reaches it.
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) {
            return;
          }
          observer.unobserve(entry.target);
          loadBokehOutput(entry.target);
        });
      },
      { rootMargin: "300px 0px" }
    );
    outputs.forEach(function (output) {
      observer.observe(output);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
