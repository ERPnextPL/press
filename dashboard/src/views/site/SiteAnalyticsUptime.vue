<template>
	<Card title="Uptime" :subtitle="subtitle" :loading="loading">
		<div
			v-if="!data || data[0].date === undefined"
			class="flex h-full items-center justify-center"
		>
			<div class="text-base text-gray-600">No data</div>
		</div>
		<div v-else class="mt-8" v-for="type in uptimeTypes" :key="type.key">
			<div class="flex h-10 justify-between">
				<div
					v-for="d in data"
					:key="d.date"
					class="w-1.5 rounded"
					:class="[
						d[type.key] === undefined
							? 'bg-white'
							: d[type.key] === 1
							? 'bg-green-500'
							: d[type.key] >= 0.90
							? 'bg-lime-500'
							: d[type.key] === 0 || d[type.key] < 0.3
							? 'bg-red-500'
							: d[type.key] >= 0.3 && d[type.key] <= 0.6
							? 'bg-orange-400'
							: 'bg-yellow-500',
					]"
					:title="
						d[type.key]
							? `${formatDate(d.date)} | Uptime: ${(d.value * 100).toFixed(2)}%`
							: ''
					"
				></div>
			</div>
		</div>
	</Card>
</template>
<script>
import { DateTime } from 'luxon';
export default {
	name: 'SiteAnalyticsUptime',
	props: ['data', 'loading'],
	computed: {
		uptimeTypes() {
			return [{ key: 'value', label: 'Web' }];
		},
		subtitle() {
			if (!this.data) return '';

			let total = 0;
			let i = 0;
			for (; i < this.data.length; i++) {
				// there could be empty objects at the end of the array
				// so we don't have to count them
				if (typeof this.data[i].value !== 'number') break;

				total += this.data[i].value;
			}
			const average = ((total / i) * 100).toFixed(2);

			return !isNaN(average) ? `Average: ${average}%` : '';
		}
	},
	methods: {
		formatDate(date) {
			return DateTime.fromSQL(date).toLocaleString(DateTime.DATETIME_FULL);
		}
	}
};
</script>
