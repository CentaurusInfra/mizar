// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file transit_log.h
 * @author Sherif Abdelwahab (@zasherif)
 *
 * @brief Logging helpers.
 *
 * @copyright Copyright (c) 2019 The Authors.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 */
#pragma once
#pragma GCC system_header

#include <syslog.h>

#define UNUSED(x) (void)(x)
#define QUOTE(...) #__VA_ARGS__

#define TEST_CASE(x)                                                                                           \
	do {                                                                                                   \
		printf("\n--------------------------------------------------------------------------------\n"  \
		       "Test: %s"                                                                              \
		       "\n--------------------------------------------------------------------------------\n", \
		       x);                                                                                     \
	} while (0)

#define TRN_LOG_INIT(entity)                                                   \
	do {                                                                   \
		openlog(entity, LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);  \
	} while (0)

#define TRN_LOG_CLOSE()                                                        \
	do {                                                                   \
		closelog();                                                    \
	} while (0)

/* debug-level message */
#define TRN_LOG_DEBUG(f_, ...)                                                 \
	do {                                                                   \
		syslog(LOG_DEBUG, "[%s:%d] " f_, __func__, __LINE__,           \
		       ##__VA_ARGS__);                                         \
	} while (0)

/* informational message */
#define TRN_LOG_INFO(f_, ...)                                                  \
	do {                                                                   \
		syslog(LOG_INFO, f_, ##__VA_ARGS__);                           \
	} while (0)

/* normal, but significant, condition */
#define TRN_LOG_NOTICE(f_, ...)                                                \
	do {                                                                   \
		syslog(LOG_NOTICE, f_, ##__VA_ARGS__);                         \
	} while (0)

/* warning conditions */
#define TRN_LOG_WARN(f_, ...)                                                  \
	do {                                                                   \
		syslog(LOG_WARNING, f_, ##__VA_ARGS__);                        \
	} while (0)

/* error conditions */
#define TRN_LOG_ERROR(f_, ...)                                                 \
	do {                                                                   \
		syslog(LOG_ERR, f_, ##__VA_ARGS__);                            \
	} while (0)

/* critical conditions */
#define TRN_LOG_CRIT(f_, ...)                                                  \
	do {                                                                   \
		syslog(LOG_CRIT, f_, ##__VA_ARGS__);                           \
	} while (0)

/* action must be taken immediately */
#define TRN_LOG_ALERT(f_, ...)                                                 \
	do {                                                                   \
		syslog(LOG_ALERT, f_, ##__VA_ARGS__);                          \
	} while (0)

/* system is unusable */
#define TRN_LOG_EMERG(f_, ...)                                                 \
	do {                                                                   \
		syslog(LOG_EMERG, f_, ##__VA_ARGS__);                          \
	} while (0)
