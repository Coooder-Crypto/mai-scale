const $ = (id) => document.getElementById(id);
const keys = ["object-name", "object-length", "object-width", "object-height", "food-name", "food-length", "food-width", "food-height"];
let dataSource = "demo";

function readPositive(id, required = false) {
  const raw = $(id).value.trim();
  if (!raw && !required) return null;
  const value = Number(raw);
  if (!raw || !Number.isFinite(value) || value <= 0) throw new Error("请填写大于 0 的有效尺寸");
  return value;
}

function ratioText(value) {
  return new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 2 }).format(value);
}

function unitEmoji(name) {
  if (name.includes("薯条")) return "🍟";
  if (name.includes("鸡")) return "🍗";
  if (name.includes("饮") || name.includes("可乐") || name.includes("咖啡")) return "🥤";
  return "🍔";
}

function calculate() {
  const error = $("error");
  error.textContent = "";
  try {
    const objectName = $("object-name").value.trim() || "这个物体";
    const foodName = $("food-name").value.trim();
    if (!foodName) throw new Error("请输入餐品名称");
    const obj = [readPositive("object-length", true), readPositive("object-width"), readPositive("object-height")];
    const food = [readPositive("food-length", true), readPositive("food-width"), readPositive("food-height")];
    if (obj[2] !== null && obj[1] === null) throw new Error("填写物体高度前，请先填写宽度");
    if (food[2] !== null && food[1] === null) throw new Error("填写餐品高度前，请先填写宽度");

    const length = obj[0] / food[0];
    const phrase = `${objectName}的长度，约等于 ${ratioText(length)} 个${foodName}排成一列。`;
    $("result-number").textContent = ratioText(length);
    $("result-food").textContent = foodName;
    $("result-sentence").textContent = phrase;

    const icon = unitEmoji(foodName);
    const count = Math.min(12, Math.max(1, Math.round(length)));
    $("visual").textContent = icon.repeat(count) + (length > 12 ? " …" : "");

    const extras = [];
    if (obj[1] !== null && food[1] !== null) {
      extras.push(["宽度", `${ratioText(obj[1] / food[1])} 个并排`]);
      extras.push(["面积", `${ratioText((obj[0] * obj[1]) / (food[0] * food[1]))} 个标尺占地`]);
      if (obj[2] !== null && food[2] !== null) {
        extras.push(["高度", `${ratioText(obj[2] / food[2])} 个叠高`]);
        extras.push(["体积", `${ratioText((obj[0] * obj[1] * obj[2]) / (food[0] * food[1] * food[2]))} 个标尺外接盒`]);
      }
    }
    const container = $("extra-ratios");
    container.replaceChildren();
    for (const [label, value] of extras) {
      const box = document.createElement("div");
      const small = document.createElement("span");
      const strong = document.createElement("strong");
      small.textContent = label;
      strong.textContent = value;
      box.append(small, strong);
      container.append(box);
    }
    $("result").hidden = false;
    window.localStorage.setItem("mai-scale-inputs", JSON.stringify(Object.fromEntries(keys.map(key => [key, $(key).value]))));
    $("result").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) {
    error.textContent = e.message;
    $("result").hidden = true;
  }
}

async function loadFoods() {
  const badge = $("source-badge");
  try {
    const response = await fetch("/api/foods");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "读取失败");
    dataSource = data.source;
    const list = $("food-options");
    list.replaceChildren();
    for (const food of data.foods) {
      const option = document.createElement("option");
      option.value = food;
      list.append(option);
    }
    badge.textContent = dataSource === "mcp"
      ? `● 已连接麦当劳 MCP · ${data.foods.length} 个餐品名称` : "○ 演示模式 · 尚未连接麦当劳 MCP";
    badge.classList.toggle("connected", dataSource === "mcp");
    $("connect-toggle").hidden = dataSource === "mcp";
    if (dataSource === "mcp" && $("food-name").value === "汉堡（演示）") {
      $("food-name").value = "";
      $("food-length").value = "";
    }
  } catch (e) {
    badge.textContent = `○ ${e.message}`;
    badge.classList.add("failed");
  }
}

$("connect-toggle").addEventListener("click", () => {
  $("connect-form").hidden = !$("connect-form").hidden;
  if (!$("connect-form").hidden) $("mcp-token").focus();
});
$("connect-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const tokenInput = $("mcp-token");
  const button = $("connect-form").querySelector("button");
  const error = $("connect-error");
  error.textContent = "";
  button.disabled = true;
  button.textContent = "连接中…";
  try {
    const response = await fetch("/api/connect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: tokenInput.value.trim() }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "连接失败");
    tokenInput.value = "";
    $("connect-form").hidden = true;
    await loadFoods();
  } catch (e) {
    tokenInput.value = "";
    error.textContent = e.message;
  } finally {
    button.disabled = false;
    button.textContent = "验证连接";
  }
});

$("calculate").addEventListener("click", calculate);
$("copy").addEventListener("click", async () => {
  const text = `${$("result-sentence").textContent}\n尺寸由用户实测，趣味换算，非官方产品尺寸。`;
  try {
    await navigator.clipboard.writeText(text);
    $("copy").textContent = "已复制 ✓";
    setTimeout(() => $("copy").textContent = "复制文案", 1800);
  } catch {
    $("copy").textContent = "复制失败";
  }
});
try {
  const saved = JSON.parse(window.localStorage.getItem("mai-scale-inputs") || "null");
  if (saved) for (const key of keys) if (typeof saved[key] === "string") $(key).value = saved[key];
} catch { /* Ignore corrupted local preferences. */ }
loadFoods();
