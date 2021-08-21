import SvgCanvas from "/svgedit-5.1.0/editor/svgcanvas.js";

const container = document.querySelector("#canvas");
const {width, height} = {width: Math.min($(window).width() - 120, 999), height: 400};
window.width = width;
window.height = height;

const config = {
	initFill: {color: "ffffff", opacity: 1},
	initStroke: {color: "000000", opacity: 1, width: 1},
	text: {stroke_width: 0, font_size: 24, font_family: "serif"},
	initOpacity: 1,
	imgPath: "/svgedit-5.1.0/editor/images/",
	dimensions: [width, height],
	baseUnit: "px"
};

window.canvas = new SvgCanvas(container, config);

canvas.textActions.setInputElem(document.querySelector("#text-input"));
$("#text-input").on("keyup input", function () {
	canvas.setTextContent(this.value);
}).on("blur", function() {
	$(this).val("");
});

let stroke = function(color) {
	canvas.getSelectedElems().forEach((el) => {
		el.setAttribute("stroke", color);
	});
};
let strokeWidth = function(width) {
	canvas.getSelectedElems().forEach((el) => {
		el.setAttribute("stroke-width", width);
	});
};
let fill = function(color) {
	canvas.getSelectedElems().forEach((el) => {
		el.setAttribute("fill", color);
	});
};


$("#select").click(() => canvas.setMode("select"));
$("#delete").click(() => canvas.deleteSelectedElements());
$("#pen").click(() => canvas.setMode("fhpath"));
$("#line").click(() => canvas.setMode("line"));
$("#curve").click(() => canvas.setMode("path"));
$("#rect").click(() => canvas.setMode("rect"));
$("#ellipse").click(() => canvas.setMode("ellipse"));
$("#text").click(() => canvas.setMode("text"));
$("#fill").click(() => fill("#" + (prompt("Enter hex color value") || "").replace(/[^0-9a-f]+/i, "")));
$("#stroke").click(() => stroke("#" + (prompt("Enter hex color value") || "").replace(/[^0-9a-f]+/i, "")));
$("#clear").click(() => { canvas.clear(); canvas.updateCanvas(width, height); });
$("#show").click(() => console.log(canvas.getSvgString()));

canvas.updateCanvas(width, height);


let uuidTo5Colors = (id) => {
	const str = id.replaceAll('-', '');
	if(!/^[0-9a-f]{32}$/i.test(str))
		return ["#000", "#000", "#000", "#000", "#000"];
	let colors = [];
	for(var i = 0; i < 30; i += 6)
		colors.push("#" + str.slice(i, i + 6));
	return colors;
};
let uuidToLogo = id => {
	const colors = uuidTo5Colors(id);
	return '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 512 512"><path d="M66.338 464.62V199.107c0-104.747 84.916-189.66 189.66-189.66h.003c104.747 0 189.66 84.913 189.66 189.66v264.247c0 17.651-11.493 34.038-28.673 38.102-24.652 5.833-46.635-12.401-47.181-35.937-.44-18.961-14.101-36.088-32.911-38.505-22.46-2.889-41.714 13.89-42.905 35.484-1.07 19.397-13.701 37.26-32.969 39.733-22.457 2.881-41.704-13.896-42.895-35.488-1.07-19.397-13.701-37.257-32.969-39.731-22.531-2.891-41.831 14.004-42.906 35.697-.943 18.989-13.17 36.493-31.962 39.381-23.616 3.629-43.952-14.545-43.952-37.47z" fill="'
		+ colors[0] +
		'"/><g fill="'
		+ colors[1] +
		'"><path d="M278.967 427.014c-22.46-2.889-41.714 13.891-42.905 35.484-.53 9.613-3.904 18.846-9.513 26.019 7.921 9.751 20.579 15.497 34.471 13.714 19.268-2.473 31.899-20.336 32.969-39.733.461-8.355 3.634-15.982 8.642-22.035-5.841-7.164-14.082-12.219-23.664-13.449zM127.231 427.011C104.7 424.12 85.4 441.016 84.324 462.708c-.475 9.572-3.821 18.765-9.426 25.9 8.116 9.926 21.153 15.67 35.391 13.482 18.792-2.889 31.019-20.393 31.962-39.381.412-8.316 3.511-15.921 8.435-21.983-5.708-7.301-13.736-12.467-23.455-13.715zM256.001 9.447H256c-9.848 0-19.519.752-28.962 2.199 90.999 13.944 160.697 92.562 160.697 187.461v264.249c0 9.486-3.323 18.603-9.061 25.643 8.758 10.428 23.021 16.077 38.315 12.459 17.179-4.064 28.673-20.449 28.673-38.102v-264.25C445.661 94.36 360.746 9.447 256.001 9.447z"/></g><g fill="'
		+ colors[2] +
		'"><circle cx="186.876" cy="217.49" r="44.674"/><circle cx="322.375" cy="217.49" r="44.675"/></g><g fill="'
		+ colors[3] +
		'"><circle cx="339.4" cy="235.158" r="20.845"/><circle cx="201.723" cy="235.838" r="20.845"/></g><g fill="#fff"><path d="M107.883 384.48a9.445 9.445 0 01-9.445-9.445v-42.737a9.445 9.445 0 0118.89 0v42.737a9.444 9.444 0 01-9.445 9.445zM107.883 311.441a9.445 9.445 0 01-9.445-9.445v-5.195a9.445 9.445 0 0118.89 0v5.195a9.445 9.445 0 01-9.445 9.445z"/></g><g fill="'
		+ colors[4] +
		'"><path d="M132.76 217.484c0 31.352 25.507 56.859 56.859 56.859s56.859-25.507 56.859-56.859-25.507-56.859-56.859-56.859-56.859 25.506-56.859 56.859zm66.304 18.354c0-4.912 3.997-8.909 8.908-8.909 4.912 0 8.909 3.997 8.909 8.909 0 4.911-3.997 8.908-8.909 8.908-4.911 0-8.908-3.996-8.908-8.908zm28.491-19.709c-5.028-4.997-11.951-8.09-19.583-8.09-15.328 0-27.797 12.471-27.797 27.799 0 7.631 3.093 14.553 8.088 19.582-20.31-.718-36.615-17.454-36.615-37.936 0-20.937 17.033-37.97 37.97-37.97 20.483 0 37.22 16.304 37.937 36.615zM265.521 217.484c0 31.352 25.507 56.859 56.859 56.859 31.354 0 56.861-25.507 56.861-56.859s-25.508-56.859-56.861-56.859c-31.354 0-56.859 25.506-56.859 56.859zm66.303 19.257c0-5.411 4.402-9.812 9.814-9.812 5.411 0 9.812 4.401 9.812 9.812s-4.401 9.812-9.812 9.812-9.814-4.401-9.814-9.812zm28.432-21.817c-5.017-4.288-11.517-6.884-18.618-6.884-15.827 0-28.703 12.876-28.703 28.701 0 7.1 2.597 13.601 6.884 18.617-19.746-1.322-35.41-17.799-35.41-37.874 0-20.937 17.033-37.97 37.97-37.97 20.077 0 36.555 15.664 37.877 35.41z"/><path d="M66.339 349.476a9.444 9.444 0 009.445-9.445V199.103c0-99.371 80.844-180.214 180.217-180.214 99.371 0 180.214 80.843 180.214 180.214a9.444 9.444 0 009.445 9.445 9.444 9.444 0 009.445-9.445C455.104 89.318 365.786 0 255.998 0 146.212 0 56.895 89.318 56.895 199.103v140.928a9.443 9.443 0 009.444 9.445zM445.659 330.587a9.444 9.444 0 00-9.445 9.445v123.32c0 13.819-9 25.978-21.401 28.911-8.835 2.092-17.53.287-24.478-5.08-6.847-5.286-10.888-13.263-11.088-21.885-.56-24.225-18.251-44.712-41.148-47.654-13.319-1.714-26.291 2.029-36.52 10.539-10.096 8.398-16.298 20.715-17.019 33.792-1.011 18.321-13.211 29.407-24.74 30.885-8.054 1.035-15.878-1.214-22.026-6.33-6.072-5.053-9.803-12.457-10.238-20.31-1.393-25.264-18.718-45.693-41.197-48.578-13.366-1.714-26.373 2.06-36.615 10.631-10.104 8.456-16.275 20.836-16.926 33.965-.666 13.435-9.111 28.232-23.96 30.514-8.508 1.305-16.713-1.002-23.124-6.503a28.474 28.474 0 01-9.948-21.632v-68.862c0-5.217-4.227-9.445-9.445-9.445s-9.445 4.227-9.445 9.445v68.865a47.348 47.348 0 0016.538 35.968c10.504 9.013 24.459 12.96 38.293 10.837 22.287-3.426 38.719-23.268 39.958-48.248.392-7.887 4.103-15.327 10.183-20.415 6.157-5.153 14.003-7.418 22.088-6.38 11.53 1.48 23.731 12.563 24.741 30.881.72 13.075 6.922 25.391 17.015 33.789 8.608 7.163 19.157 10.951 30.228 10.951 2.079 0 4.178-.133 6.285-.404 22.478-2.886 39.802-23.318 41.196-48.58.433-7.854 4.166-15.257 10.239-20.311 6.149-5.115 13.974-7.362 22.031-6.325 13.72 1.763 24.325 14.383 24.673 29.358.334 14.344 7.049 27.611 18.426 36.396 11.379 8.789 26.092 11.888 40.374 8.513 20.826-4.926 35.942-24.815 35.942-47.293v-123.32c-.002-5.221-4.229-9.45-9.447-9.45zM445.659 249.428a9.444 9.444 0 00-9.445 9.445v13.973a9.444 9.444 0 009.445 9.445 9.444 9.444 0 009.445-9.445v-13.973a9.444 9.444 0 00-9.445-9.445z"/></g></svg>';
};

let update = (json) => {
	let $body = $(".list")[0];
	while($body.lastElementChild){$body.removeChild($body.lastElementChild);}
	let template = $("#list-template")[0].content;
	let $td = template.querySelectorAll("td");
	for(var i = 0; i < json.length; i++) {
		var item = json[i];
		$td[0].innerHTML = uuidToLogo(item.userId);
		$td[1].textContent = item.date.replace(/\..*$/, '').replace('T', ' ');
		$td[2].textContent = item.fileId;
		$td[3].firstChild.href = "/api/svg?userId=" + encodeURIComponent(item.userId) + "&fileId=" + encodeURIComponent(item.fileId);
		($td[3].firstChild.classList)[json[i].userId !== window["me"] ? "add" : "remove"]("hidden");
		$td[4].firstChild.href = "/api/pdf?userId=" + encodeURIComponent(item.userId) + "&fileId=" + encodeURIComponent(item.fileId);
		let clone = document.importNode(template, true);
		$body.appendChild(clone);
	}
};

let error = (text) => alert(text);

$(document).on("click", "a.link-pdf", function() {
	open($(this).prop("href"), "Preview", "toolbar=no,menubar=no,width=600,height=300,left=120,top=180");
	return false;
});
$(document).on("click", "a.link-svg", function() {
	open($(this).prop("href"), "Source", "toolbar=no,menubar=no,width=600,height=300,left=120,top=180");
	return false;
});

fetch("/api/me", {"credentials":"same-origin"}).then(response => {
	if(!response.ok) response.text().then(text => { error(text); });
	response.text().then(text => {
		window.me = text;
		$(".login").html(uuidToLogo(text));
		fetch("/api/list?skip=0&take=20").then(response => {
			response.json().then(update);
		}).catch(() => error("/api/list failed"));
	});
}).catch(() => error("/api/me failed"));

$("#upload").click(function(e) {
	$.post("/api/svg", {data: canvas.getSvgString()});
	setTimeout(() => fetch("/api/list?skip=0&take=20").then(response => {
		response.json().then(update);
	}).catch(() => error("/api/list failed")), 100);
});

$("#canvas").mousedown(() => $(document).scrollTop(0));
