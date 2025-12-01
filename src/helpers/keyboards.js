export function mkKeyboard(arr, wrap = 2) {
  // arr: array of { text, callback_data } or strings
  const buttons = arr.map(item => {
    if (typeof item === "string") return { text: item, callback_data: item };
    return item;
  });

  const rows = [];
  for (let i = 0; i < buttons.length; i += wrap) {
    rows.push(buttons.slice(i, i + wrap));
  }
  return { reply_markup: JSON.stringify({ inline_keyboard: rows }) };
}
