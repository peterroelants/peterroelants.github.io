function parseURL(url) {
  return $('<a>', {href: url});
}

function getCurrentPageIdx() {
  return $(".pagination-container div[page-idx]:visible").attr("page-idx")
}

function togglePage(page_idx) {
  all_pages = $(".pagination-container div.page-content").each(function() {
    let idx = $(this).attr("page-idx")
    if (page_idx === idx) {
      $(this).show();
    } else {
      $(this).hide();
    }
  });
}

function showPage(page_idx) {
  let current_page_idx = getCurrentPageIdx()
  if (page_idx !== current_page_idx) {
    togglePage(page_idx)
  }
}

function pageChange(elem) {
  let page_idx = $(elem).parent().attr("page-idx");
  showPage(page_idx)
}

function addPageLinkHandlers() {
  let page_links = $("ul.pagination li.page-item a.page-link");
  page_links.on('click.pageChange',function(e){
    e.preventDefault();
    pageChange(this)
    });
}

function localLinkHandler() {
  let url = window.location.toString();
  let hash_item = parseURL(url).prop('hash')
  if (hash_item) {
    var hash_page_idx = $(hash_item).closest('div.page-content').attr("page-idx")
    showPage(hash_page_idx);
    // Blink
    $(hash_item).get(0).scrollIntoView();
    $(hash_item)
      .find('a')
      .delay(150)
      .fadeIn(750)
      .delay(200)
      .fadeOut(750)
      .delay(10, complete=function(){
        $(this).removeAttr("style");
      })
  }
}

// Register page-nav click handler
$(document).ready(addPageLinkHandlers);
// Switch to page to show local hashed URL (if provided)
$(window).on("load", localLinkHandler);
// Switch to page when local link (hash-part of url) has changed
$(window).on('hashchange', localLinkHandler);
