module.exports = {
  plugins: [
    // Add vendor prefixes automatically
    require('autoprefixer'),
    
    // Minify CSS with controlled optimization to prevent shorthand conflicts
    require('cssnano')({
      preset: ['default', {
        // Prevent merging individual properties into shorthand
        // This avoids the overflow-x/overflow-y vs overflow shorthand conflict
        mergeLonghand: false,
        
        // Be conservative with rule merging to maintain specificity
        mergeRules: false,
        
        // Keep individual values separate (e.g., don't merge margin-top, margin-bottom)
        mergeIdents: false,
        
        // Other safe optimizations
        discardComments: { removeAll: true },
        normalizeWhitespace: true,
        colormin: true,
        convertValues: true,
        discardDuplicates: true,
        discardEmpty: true,
        minifyFontValues: true,
        minifyParams: true,
        minifySelectors: true,
        normalizeCharset: true,
        normalizeDisplayValues: true,
        normalizePositions: true,
        normalizeRepeatStyle: true,
        normalizeString: true,
        normalizeTimingFunctions: true,
        normalizeUnicode: true,
        normalizeUrl: true,
        orderedValues: true,
        reduceIdents: true,
        reduceInitial: true,
        reduceTransforms: true,
        svgo: true,
        uniqueSelectors: true
      }]
    })
  ]
}
