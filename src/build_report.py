# -*- coding: utf-8 -*-
"""渲染最终 HTML 舆情分析报告（ECharts 暗色看板）"""
import json

with open("output/analysis_result.json", encoding="utf-8") as f:
    DATA = json.dumps(json.load(f), ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>清北鸭腿事件 · 舆情分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts-wordcloud@2.1.0/dist/echarts-wordcloud.min.js"></script>
<style>
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2129;--border:#2d333b;--txt:#e6edf3;--sub:#8b949e;
--red:#f85149;--orange:#d29922;--green:#3fb950;--blue:#58a6ff;--purple:#bc8cff;--pink:#ff7b72}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--txt);font-family:"Microsoft YaHei","PingFang SC",sans-serif;line-height:1.7}
.wrap{max-width:1180px;margin:0 auto;padding:32px 20px 60px}
header{text-align:center;padding:36px 0 26px;border-bottom:1px solid var(--border)}
h1{font-size:30px;letter-spacing:1px;background:linear-gradient(90deg,#f85149,#ff9d5c,#ffd166);-webkit-background-clip:text;background-clip:text;color:transparent}
.tagline{color:var(--sub);margin-top:10px;font-size:14px}
.badge{display:inline-block;background:var(--panel2);border:1px solid var(--border);color:var(--sub);border-radius:20px;padding:2px 14px;font-size:12px;margin:6px 4px 0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:26px 0 8px}
.kpi{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px 16px;text-align:center}
.kpi .v{font-size:26px;font-weight:700;color:#ffd166}
.kpi .l{font-size:12px;color:var(--sub);margin-top:4px}
section{margin-top:44px}
h2{font-size:20px;padding-left:12px;border-left:4px solid var(--red);margin-bottom:6px}
.desc{color:var(--sub);font-size:13px;margin-bottom:16px}
.grid{display:grid;gap:16px}
.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:1fr 1fr 1fr}
@media(max-width:860px){.g2,.g3{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:16px}
.card h3{font-size:15px;margin-bottom:8px;color:var(--txt)}
.chart{width:100%;height:340px}
.tall{height:420px}
ul.events{list-style:none}
ul.events li{position:relative;padding:0 0 18px 26px;font-size:14px}
ul.events li::before{content:"";position:absolute;left:5px;top:8px;width:9px;height:9px;border-radius:50%;background:var(--red);box-shadow:0 0 8px var(--red)}
ul.events li::after{content:"";position:absolute;left:9px;top:20px;bottom:0;width:1px;background:var(--border)}
ul.events li:last-child::after{display:none}
ul.events .d{color:var(--blue);font-weight:600;margin-right:8px}
.topic-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
@media(max-width:860px){.topic-grid{grid-template-columns:1fr}}
.topic{background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:14px}
.topic .t-share{font-size:22px;font-weight:700;color:var(--purple)}
.topic .t-name{font-size:13px;color:var(--txt);margin:2px 0 8px;font-weight:600}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:#21262d;border:1px solid #30363d;border-radius:14px;padding:1px 10px;font-size:12px;color:#c9d1d9}
.chip.top{border-color:var(--purple);color:var(--purple)}
.pie-row{display:flex;justify-content:center;gap:8px;margin-top:10px;font-size:13px}
.dot{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}
.quote{background:var(--panel2);border-left:3px solid var(--border);border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:10px;font-size:13.5px}
.quote.q-neg{border-left-color:var(--red)}.quote.q-pos{border-left-color:var(--green)}.quote.q-neu{border-left-color:var(--blue)}
.quote .meta{color:var(--sub);font-size:12px;margin-top:4px}
.summary li{margin:8px 0 8px 20px;font-size:14px}
.concl{background:linear-gradient(135deg,#1a1420,#161b22);border:1px solid #3a2a3f;border-radius:12px;padding:18px 20px;margin-top:14px}
.concl b{color:var(--pink)}
footer{margin-top:50px;padding-top:18px;border-top:1px solid var(--border);color:var(--sub);font-size:12.5px;text-align:center}
footer p{margin:4px 0}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>清北鸭腿事件 · 全链路舆情分析报告</h1>
  <div class="tagline">「鹅腿阿姨」以鸭充鹅事件｜传播 → 画像 → 话题 → 情感 → 摘要</div>
  <div>
    <span class="badge">监测窗口 2026.06.09 – 06.14</span>
    <span class="badge">方法：LDA 主题模型 / SnowNLP+情感词典 / TextRank / jieba</span>
    <span class="badge">数据：微博·抖音·小红书·头条等多平台语料</span>
  </div>
</header>

<div class="kpis" id="kpis"></div>

<section>
  <h2>一、传播概况</h2>
  <div class="desc">事件于 6 月 9 日 20 时许在团购群曝光后夜间低温发酵，6 月 10 日经热搜引爆达到峰值（单日约 12.2 万条，倒 U 型走势），6 月 11 日因市监局通报形成次峰，随后回落。</div>
  <div class="grid g2">
    <div class="card"><h3>舆情传播走势（真实全网声量 × 样本负面率）</h3><div class="chart" id="c-trend"></div></div>
    <div class="card"><h3>传播平台分布</h3><div class="chart" id="c-platform"></div></div>
  </div>
  <div class="grid g2" style="margin-top:16px">
    <div class="card"><h3>微博热搜话题榜（话题阅读量 / 万）</h3><div class="chart tall" id="c-hot"></div></div>
    <div class="card"><h3>事件时间轴</h3><div class="card" style="border:none;padding:6px 4px"><ul class="events" id="events"></ul></div></div>
  </div>
</section>

<section>
  <h2>二、群体画像</h2>
  <div class="desc">参与讨论的核心群体为在校大学生与普通路人；国贸上班族是「破防点」触发者；媒体蓝V贡献了权威信源。不同群体的情感立场差异显著：法律博主与在校生负面率最高，路人群体中同情摊主的声音更多。</div>
  <div class="grid g2">
    <div class="card"><h3>参与群体分布 × 平均情感倾向</h3><div class="chart tall" id="c-user"></div></div>
    <div class="card"><h3>讨论者地域分布 TOP10</h3><div class="chart tall" id="c-loc"></div></div>
  </div>
  <div class="grid g3" style="margin-top:16px" id="persona"></div>
</section>

<section>
  <h2>三、话题分析（LDA 主题模型）</h2>
  <div class="desc">对全部语料分词后，使用 sklearn LDA（6 主题）提取潜在话题结构。高频词云与主题分布显示：「欺诈追责」「食品安全（发绿腿）」「群体讽刺」构成三大舆论主干。</div>
  <div class="grid g2">
    <div class="card"><h3>高频关键词词云</h3><div class="chart tall" id="c-wordcloud"></div></div>
    <div class="card"><h3>LDA 六大主题及占比</h3><div class="topic-grid" style="grid-template-columns:1fr 1fr" id="topics"></div></div>
  </div>
</section>

<section>
  <h2>四、情感与数据分析</h2>
  <div class="desc">SnowNLP 语义打分叠加情感词典修正（强化欺诈/变质等负向词）。整体情感呈显著负向，正面声音主要来自「同情小贩」与「玩梗二创」群体。</div>
  <div class="grid g3">
    <div class="card"><h3>整体情感分布</h3><div class="chart tall" id="c-pie"></div></div>
    <div class="card"><h3>分平台情感构成</h3><div class="chart tall" id="c-stacked"></div></div>
    <div class="card">
      <h3>典型评论样本</h3>
      <div id="examples" style="max-height:420px;overflow:auto"></div>
    </div>
  </div>
</section>

<section>
  <h2>五、核心结论（TextRank 摘要 + 分析观点）</h2>
  <div class="card">
    <h3>📊 文本摘要（TextRank 自动抽取的高权重观点句）</h3>
    <ul class="summary" id="summary"></ul>
  </div>
  <div class="concl">
    <h3 style="margin-bottom:10px">🧭 舆情研判结论</h3>
    <p><b>① 舆情本质：</b>这不是一次普通的消费纠纷，而是「情感信任透支」引发的信任反噬事件。学生群体是鹅腿阿姨口碑的缔造者，曝光后「情怀背刺」感放大了传播势能。</p>
    <p style="margin-top:6px"><b>② 传播机制：</b>正面人设的彻底反转自带极强冲突性，「最聪明的学生被骗八年」「官媒+高校背书却无人查验食材」等反差叙事被平台反复推送，形成热搜连环引爆。</p>
    <p style="margin-top:6px"><b>③ 议题升级路径：</b>以鸭充鹅（欺诈）→ 发绿肉质（食品安全）→ 其子言论（当事人失格）→ 优绩主义与造神反思（社会议题），四级议题逐层外溢，峰值持续时间长。</p>
    <p style="margin-top:6px"><b>④ 管理建议：</b>对商家——主动标注食材、公开资质、退一赔三止损；对监管部门——建立网红摊贩长效抽检机制，填补私域团购监管盲区；对平台——对「情怀滤镜」类内容加强资质核验，避免造神式推流。</p>
  </div>
</section>

<footer>
  <p><b>数据与方法说明</b></p>
  <p>微博搜索接口需登录态，本报告语料为「半真实」构造：事件事实、时间线、热搜阅读量、平台占比与总声量均取自真实公开报道（新华社/澎湃/红星/拓尔思网察/瑞智大数据等）；语料库含 607 条媒体报道引用的真实网民评论原话，其余为按真实立场分布生成的演示样本，全流程（分词→LDA→情感→摘要→可视化）为完整可复现管线。</p>
  <p>项目目录：qingbei-duckleg-sentiment｜爬虫脚本 spider_weibo.py 配置 Cookie 后可接入实时真实数据，分析代码无需改动。</p>
</footer>
</div>

<script>
const D = __DATA__;
const NEG="#f85149",POS="#3fb950",NEU="#58a6ff",ORANGE="#d29922",PURPLE="#bc8cff";
const charts=[];
function mk(id,opt){const c=echarts.init(document.getElementById(id),null,{renderer:'canvas'});c.setOption(opt);charts.push(c);}
window.addEventListener('resize',()=>charts.forEach(c=>c.resize()));

// KPI
const totalAll = D.timeline.reduce((s,t)=>s+t.volume,0);
const peak = Math.max(...D.timeline.map(t=>t.volume));
const neg = D.sentiment_overall.find(x=>x.name==='负面')||{value:0};
const pos = D.sentiment_overall.find(x=>x.name==='正面')||{value:0};
const neu = D.sentiment_overall.find(x=>x.name==='中性')||{value:0};
const top1n = D.hot_topics.filter(h=>h.rank===1).length;
const wb = D.platform.find(p=>p.name.includes('微博'));
const kpis=[["21万+", "全网总信息量(条)"],[peak.toLocaleString(), "峰值单日声量(6/10)"],
[top1n, "登顶热搜TOP1话题数"],[(wb?wb.value/D.meta.sample_n*100:0).toFixed(1)+"%", "微博渠道占比"],
[(neg.value/(neg.value+neu.value+pos.value)*100).toFixed(1)+"%", "样本负面情绪占比"]];
document.getElementById('kpis').innerHTML=kpis.map(k=>`<div class="kpi"><div class="v">${k[0]}</div><div class="l">${k[1]}</div></div>`).join('');

// 1 走势
mk('c-trend',{tooltip:{trigger:'axis'},legend:{textStyle:{color:'#8b949e'},data:['全网声量','负面率%']},
grid:{left:60,right:55,bottom:30,top:40},
xAxis:{type:'category',data:D.timeline.map(t=>t.date),axisLabel:{color:'#8b949e'},axisLine:{lineStyle:{color:'#2d333b'}}},
yAxis:[{type:'value',name:'条',nameTextStyle:{color:'#8b949e'},axisLabel:{color:'#8b949e'},splitLine:{lineStyle:{color:'#1c2129'}}},
{type:'value',name:'负面率%',max:100,nameTextStyle:{color:'#8b949e'},axisLabel:{color:'#8b949e'},splitLine:{show:false}}],
series:[
{name:'全网声量',type:'bar',data:D.timeline.map(t=>t.volume),barWidth:'45%',itemStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#f85149'},{offset:1,color:'#7a1f1c'}])}},
{name:'负面率%',type:'line',yAxisIndex:1,smooth:true,data:D.timeline.map(t=>t.neg),lineStyle:{color:'#ffd166',width:2.5},itemStyle:{color:'#ffd166'},areaStyle:{color:'rgba(255,209,102,0.08)'}}]});

// 2 平台
mk('c-platform',{tooltip:{trigger:'item',formatter:'{b}: {c} 条 ({d}%)'},
series:[{type:'pie',radius:['42%','70%'],center:['50%','52%'],data:D.platform.map((p,i)=>({name:p.name,value:p.value,
itemStyle:{color:['#f85149','#d29922','#58a6ff','#bc8cff','#3fb950','#ff7b72'][i%6]}})),
label:{color:'#8b949e',fontSize:12},itemStyle:{borderColor:'#0d1117',borderWidth:2}}]});

// 3 热搜
const ht=[...D.hot_topics].sort((a,b)=>a.reads-b.reads);
mk('c-hot',{tooltip:{formatter:p=>p.name+'<br>阅读量 '+p.value+' 万'+(ht[p.dataIndex]?` · 最高第${ht[p.dataIndex].rank}位`:'')},
grid:{left:230,right:60,top:10,bottom:20},
xAxis:{type:'value',axisLabel:{color:'#8b949e'},splitLine:{lineStyle:{color:'#1c2129'}}},
yAxis:{type:'category',data:ht.map(h=>h.topic),axisLabel:{color:'#c9d1d9',fontSize:12},axisLine:{lineStyle:{color:'#2d333b'}}},
series:[{type:'bar',data:ht.map(h=>h.reads),barWidth:14,itemStyle:{borderRadius:[0,7,7,0],color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#7a1f1c'},{offset:1,color:'#f85149'}])},
label:{show:true,position:'right',color:'#8b949e',fontSize:11,formatter:'{c}万'}}]});

// 4 时间轴
document.getElementById('events').innerHTML=D.events.map(e=>`<li><span class="d">${e.date}</span>${e.text}</li>`).join('');

// 5 群体
const ut=[...D.user_type].sort((a,b)=>b.value-a.value);
mk('c-user',{tooltip:{trigger:'axis'},legend:{textStyle:{color:'#8b949e'}},
grid:{left:200,right:70,top:36,bottom:20},
xAxis:[{type:'value',name:'条数',axisLabel:{color:'#8b949e',fontSize:10},splitLine:{lineStyle:{color:'#1c2129'}}},
{type:'value',name:'负面率%',max:100,axisLabel:{color:'#8b949e',fontSize:10},splitLine:{show:false}}],
yAxis:{type:'category',data:ut.map(u=>u.name),axisLabel:{color:'#c9d1d9',fontSize:12},axisLine:{lineStyle:{color:'#2d333b'}}},
series:[
{name:'讨论量',type:'bar',data:ut.map(u=>u.value),barWidth:12,itemStyle:{color:'#58a6ff',borderRadius:[0,6,6,0]}},
{name:'负面率%',type:'scatter',xAxisIndex:1,data:ut.map(u=>[u.neg_ratio,ut.indexOf(u)]),symbolSize:14,itemStyle:{color:'#f85149'}}]});

// 6 地域
mk('c-loc',{tooltip:{},grid:{left:70,right:40,top:10,bottom:20},
xAxis:{type:'value',axisLabel:{color:'#8b949e'},splitLine:{lineStyle:{color:'#1c2129'}}},
yAxis:{type:'category',data:D.location.map(l=>l.name).reverse(),axisLabel:{color:'#c9d1d9'},axisLine:{lineStyle:{color:'#2d333b'}}},
series:[{type:'bar',data:D.location.map(l=>l.value).reverse(),barWidth:13,itemStyle:{color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#1f3a5f'},{offset:1,color:'#58a6ff'}]),borderRadius:[0,6,6,0]},label:{show:true,position:'right',color:'#8b949e',fontSize:11}}]});

// 7 画像卡片
const personas=[
["🎓 在校大学生（清北人为主）","占比最大的发声群体，情绪以「信任背刺」为主：自嘲被骗八年、晒腹泻经历、组织集体诉讼，负面对抗性最强。"],
["💼 国贸上班族 / 白领","事件触发者。被阿姨群公告称为「上班精英」，部分人反感其举报行为，但主流舆论支持其维权，是议题外溢的引爆点。"],
["⚖️ 法律/时评博主","聚焦消保法退一赔三、虚假宣传定性、偷税与检疫问题，负面率高但论述理性，推动议题走向制度化讨论。"],
["📰 媒体蓝V","新华社、澎湃、中新网、极目等持续跟踪，提供权威信源与评论框架，「网红美食没有豁免权」成为定调句。"],
["🍢 同情摊主阵营","「老婆饼里没老婆」「小本生意不容易」，呼吁给底层小贩留生路，与追责阵营形成观点对冲。"],
["🤳 玩梗/二创群体","「鸭骗战争」「鹅门」「朝阳群众从未翻车」等梗加速破圈传播，是热度长尾的主要贡献者。"]];
document.getElementById('persona').innerHTML=personas.map(p=>`<div class="card"><h3>${p[0]}</h3><div style="font-size:13px;color:#8b949e">${p[1]}</div></div>`).join('');

// 8 词云
mk('c-wordcloud',{series:[{type:'wordCloud',shape:'circle',width:'92%',height:'92%',
sizeRange:[13,52],rotationRange:[-45,45],gridSize:6,drawOutOfBound:false,
textStyle:{fontFamily:'Microsoft YaHei',color:()=>['#f85149','#ffd166','#58a6ff','#bc8cff','#3fb950','#ff7b72'][Math.floor(Math.random()*6)]},
data:D.wordcloud}]});

// 9 LDA 主题
document.getElementById('topics').innerHTML=D.lda_topics.sort((a,b)=>b.share-a.share).map(t=>
`<div class="topic"><div class="t-share">${t.share}%</div><div class="t-name">主题 ${t.id} · ${t.words.slice(0,3).map(w=>w.w).join(' / ')}</div>
<div class="chips">${t.words.map((w,i)=>`<span class="chip${i<3?' top':''}">${w.w}</span>`).join('')}</div></div>`).join('');

// 10 情感饼
mk('c-pie',{tooltip:{trigger:'item',formatter:'{b}: {c} ({d}%)'},
series:[{type:'pie',radius:['40%','68%'],center:['50%','52%'],
data:[{name:'负面',value:neg.value,itemStyle:{color:NEG}},{name:'中性',value:neu.value,itemStyle:{color:NEU}},{name:'正面',value:pos.value,itemStyle:{color:POS}}],
label:{color:'#8b949e'},itemStyle:{borderColor:'#0d1117',borderWidth:2}}]});

// 11 分平台堆积
const plats=D.sentiment_by_platform;
mk('c-stacked',{tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},legend:{textStyle:{color:'#8b949e'}},
grid:{left:150,right:30,top:36,bottom:20},
xAxis:{type:'value',axisLabel:{color:'#8b949e'},splitLine:{lineStyle:{color:'#1c2129'}}},
yAxis:{type:'category',data:plats.map(p=>p.platform),axisLabel:{color:'#c9d1d9',fontSize:11},axisLine:{lineStyle:{color:'#2d333b'}}},
series:[['负面',NEG],['中性',NEU],['正面',POS]].map(([k,c])=>({name:k,type:'bar',stack:'s',
data:plats.map(p=>p[k]||0),barWidth:14,itemStyle:{color:c},emphasis:{focus:'series'}}))});

// 12 典型评论
const exs=[...(D.examples.neg||[]).map(e=>({...e,cls:'q-neg',lab:'负面'})),...(D.examples.neu||[]).map(e=>({...e,cls:'q-neu',lab:'中性'})),...(D.examples.pos||[]).map(e=>({...e,cls:'q-pos',lab:'正面'}))];
document.getElementById('examples').innerHTML=exs.map(e=>
`<div class="quote ${e.cls}">${e.content}<div class="meta">「${e.lab}」· ${e.user_type} · 👍 ${e.likes}</div></div>`).join('');

// 13 摘要
document.getElementById('summary').innerHTML=D.summary.map(s=>`<li>${s}</li>`).join('');
</script>
</body>
</html>"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(HTML.replace("__DATA__", DATA))
print("report.html 已生成")
