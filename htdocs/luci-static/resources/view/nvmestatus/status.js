'use strict';
'require view';
'require rpc';
'require poll';

var callSmartLog = rpc.declare({
	object: 'nvmestatus',
	method: 'smart_log',
	params: ['device']
});

var callDeviceList = rpc.declare({
	object: 'nvmestatus',
	method: 'device_list'
});

function _(str) {
	return (window.TR && window.TR[str]) ? window.TR[str] : str;
}

function getColor(type, value) {
	var v = parseFloat(value);
	if (type === 'temp') {
		if (v >= 70) return 'var(--red)';
		if (v >= 55) return 'var(--orange)';
		return 'var(--green)';
	}
	if (type === 'used') {
		if (v >= 90) return 'var(--red)';
		if (v >= 70) return 'var(--orange)';
		return 'var(--green)';
	}
	if (type === 'spare') {
		if (v <= 10) return 'var(--red)';
		if (v <= 30) return 'var(--orange)';
		return 'var(--green)';
	}
	if (type === 'err') return v === 0 ? 'var(--green)' : 'var(--red)';
	if (type === 'warn') return v > 0 ? 'var(--orange)' : 'var(--gray)';
	return 'var(--gray)';
}

function statusBadge(ok, text) {
	var color = ok ? 'var(--success)' : 'var(--danger)';
	var bg = ok ? 'rgba(45,206,137,0.12)' : 'rgba(245,54,92,0.12)';
	return '<span style="display:inline-flex;align-items:center;gap:5px;padding:2px 10px 2px 8px;border-radius:20px;background:' + bg + ';color:' + color + ';font-size:.75rem;font-weight:600">'
		+ '<span style="width:6px;height:6px;border-radius:50%;background:' + color + ';flex-shrink:0;display:inline-block"></span>' + text + '</span>';
}

function progressBar(pct, color) {
	pct = Math.min(100, Math.max(0, pct));
	return '<div style="height:4px;border-radius:2px;background:var(--lighter);margin-top:8px;overflow:hidden">'
		+ '<div style="width:' + pct + '%;height:100%;background:' + color + ';border-radius:2px;transition:width .4s ease"></div></div>';
}

function bigMetric(value, unit, label, color, pct) {
	return '<div style="flex:1;min-width:140px;background:var(--white);border-radius:.375rem;padding:1.25rem 1.5rem;box-shadow:0 0 1rem 0 rgba(136,152,170,.15)">'
		+ '<div style="font-size:2rem;font-weight:700;color:' + color + ';line-height:1">' + value
		+ '<span style="font-size:.875rem;font-weight:400;color:var(--gray);margin-left:3px">' + unit + '</span></div>'
		+ '<div style="font-size:.75rem;color:var(--gray);margin-top:4px;text-transform:uppercase;letter-spacing:.05em">' + _(label) + '</div>'
		+ progressBar(pct, color)
		+ '</div>';
}

function infoSection(title, rows) {
	var html = '<div style="background:var(--white);border-radius:.375rem;box-shadow:0 0 1rem 0 rgba(136,152,170,.15);overflow:hidden;min-width:0">';
	html += '<h3 style="font-size:.875rem;font-weight:600;color:var(--gray-dark);padding:.875rem 1.25rem;margin:0;border-bottom:1px solid var(--lighter);background:var(--secondary)">' + _(title) + '</h3>';
	rows.forEach(function(row, i) {
		html += '<div style="display:flex;justify-content:space-between;align-items:center;gap:.5rem;padding:.6rem 1.25rem;'
			+ (i < rows.length - 1 ? 'border-bottom:1px solid var(--lighter)' : '') + '">';
		html += '<span style="font-size:.8125rem;color:var(--gray);flex-shrink:0">' + _(row.label) + '</span>';
		html += '<span style="font-size:.8125rem;color:var(--gray-dark);font-weight:500;text-align:right">' + row.value + '</span>';
		html += '</div>';
	});
	html += '</div>';
	return html;
}

function loadLocale(cb) {
	var lang = (document.documentElement.lang || navigator.language || 'en').replace('-', '_');
	if (lang.indexOf('zh') === 0) lang = 'zh_Hans';
	else lang = 'en';
	if (lang === 'en') { cb(); return; }
	var s = document.createElement('script');
	s.src = '/luci-static/resources/locale/zh_Hans/luci-app-nvmestatus.js';
	s.onload = cb;
	s.onerror = cb;
	document.head.appendChild(s);
}

function renderData(data) {
	if (data.error) {
		return '<div class="alert-message error" style="margin:0">' + data.error + '</div>';
	}

	var temp = parseInt(data.temperature);
	var used = parseInt(data.percentage_used);
	var spare = parseInt(data.available_spare);
	var powOnYears = (parseInt(data.power_on_hours) / 8760).toFixed(1);
	var warnHours = Math.round(parseInt(data.warning_temp_time) / 60);
	var critHours = Math.round(parseInt(data.critical_temp_time) / 60);

	var html = '<style>'
		+ '.nvme-metrics{display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap}'
		+ '.nvme-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}'
		+ '@media(max-width:600px){.nvme-grid{grid-template-columns:1fr}}'
		+ '</style>';

	html += '<div class="nvme-metrics">';
	html += bigMetric(temp, '°C', 'Temperature', getColor('temp', temp), temp);
	html += bigMetric(used, '%', 'Life Used', getColor('used', used), used);
	html += bigMetric(spare, '%', 'Spare Available', getColor('spare', spare), spare);
	html += '</div>';

	html += '<div class="nvme-grid">';

	html += infoSection('Health Status', [
		{ label: 'Critical Warning', value: statusBadge(data.critical_warning === '0', data.critical_warning === '0' ? _('Normal') : _('Warning') + ' ' + data.critical_warning) },
		{ label: 'Media Errors', value: statusBadge(data.media_errors === '0', data.media_errors === '0' ? _('No Errors') : data.media_errors + ' ' + _('error(s)')) },
		{ label: 'Error Log Entries', value: statusBadge(data.num_err_log_entries === '0', data.num_err_log_entries === '0' ? _('No Records') : data.num_err_log_entries + ' ' + _('record(s)')) },
		{ label: 'Unsafe Shutdowns', value: '<span style="color:' + getColor('warn', data.unsafe_shutdowns) + ';font-weight:600">' + data.unsafe_shutdowns + '</span>' }
	]);

	html += infoSection('Usage Statistics', [
		{ label: 'Power On Hours', value: data.power_on_hours + ' h (' + powOnYears + ' yr)' },
		{ label: 'Power Cycles', value: data.power_cycles },
		{ label: 'Controller Busy Time', value: parseInt(data.controller_busy_time).toLocaleString() + ' min' },
		{ label: 'Spare Threshold', value: data.available_spare_threshold + '%' }
	]);

	html += infoSection('Data Throughput', [
		{ label: 'Total Read', value: data.data_units_read },
		{ label: 'Total Written', value: data.data_units_written },
		{ label: 'Read Commands', value: parseInt(data.host_read_commands).toLocaleString() },
		{ label: 'Write Commands', value: parseInt(data.host_write_commands).toLocaleString() }
	]);

	html += infoSection('Temperature History', [
		{ label: 'Current Temp', value: '<span style="color:' + getColor('temp', temp) + ';font-weight:600">' + temp + ' °C</span>' },
		{ label: 'Warning Temp Time', value: '<span style="color:' + getColor('warn', warnHours) + '">' + warnHours.toLocaleString() + ' h</span>' },
		{ label: 'Critical Temp Time', value: '<span style="color:' + (critHours > 0 ? 'var(--red)' : 'var(--gray)') + '">' + critHours.toLocaleString() + ' h</span>' },
		{ label: 'Life Used', value: '<span style="color:' + getColor('used', used) + ';font-weight:600">' + used + '%</span>' }
	]);

	html += '</div>';
	return html;
}

function doRefresh(currentDevice, container) {
	return callSmartLog(currentDevice).then(function(data) {
		if (container) {
			container.style.cssText = '';
			container.innerHTML = renderData(data);
		}
	}).catch(function(err) {
		if (container) {
			container.innerHTML = '<div class="alert-message error" style="margin:0">Failed to load data: ' + err + '</div>';
		}
	});
}

return view.extend({
	load: function() {
		return new Promise(function(resolve) {
			loadLocale(function() {
				callDeviceList().then(resolve).catch(function() { resolve(null); });
			});
		});
	},

	render: function(deviceData) {
		var devices = (deviceData && deviceData.devices) ? deviceData.devices : ['/dev/nvme0n1'];
		var currentDevice = devices[0];

		var wrapper = document.createElement('div');

		var titleRow = document.createElement('div');
		titleRow.style.cssText = 'display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;margin-bottom:.5rem';

		var title = document.createElement('h2');
		title.style.cssText = 'margin:0';
		title.textContent = _('NVMe Health Monitor');
		titleRow.appendChild(title);

		var rightBar = document.createElement('div');
		rightBar.style.cssText = 'display:flex;align-items:center;gap:.5rem;flex-wrap:wrap';

		if (devices.length > 1) {
			var sel = document.createElement('select');
			sel.className = 'cbi-input-select';
			sel.style.cssText = 'margin:0';
			devices.forEach(function(d) {
				var opt = document.createElement('option');
				opt.value = d;
				opt.textContent = d;
				sel.appendChild(opt);
			});
			sel.addEventListener('change', function() {
				currentDevice = this.value;
				doRefresh(currentDevice, container);
			});
			rightBar.appendChild(sel);
		}

		var refreshBtn = document.createElement('button');
		refreshBtn.className = 'cbi-button';
		refreshBtn.style.cssText = 'margin:0;background-color:#2dce89;border-color:#2dce89;color:#fff';
		refreshBtn.textContent = _('Refresh Now');
		refreshBtn.addEventListener('click', function() {
			doRefresh(currentDevice, container);
		});
		rightBar.appendChild(refreshBtn);

		titleRow.appendChild(rightBar);
		wrapper.appendChild(titleRow);

		var container = document.createElement('div');
		container.style.cssText = 'color:var(--gray);padding:2rem;text-align:center';
		container.textContent = _('Loading...');
		wrapper.appendChild(container);

		doRefresh(currentDevice, container);

		poll.add(function() {
			return doRefresh(currentDevice, container);
		}, 30);

		poll.start();

		return wrapper;
	},

	handleSaveApply: null,
	handleSave: null,
	handleReset: null
});
