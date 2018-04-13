function getUniqueItems(items) {
  var unique = [];
  items.forEach(function (item) {
    if (unique.indexOf(item) < 0) {
      unique.push(item);
    }
  });
  return unique;
}