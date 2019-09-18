// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_agent_xdp_usr.h
 * @author Sherif Abdelwahab (@zasherif)
 *
 * @brief Transit daemon functions and helper macros
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

#include <search.h>

#include "trn_transit_xdp_usr.h"
#include "trn_agent_xdp_usr.h"

#define INTF_INSERT()                                                                               \
	do {                                                                                        \
		ENTRY e, *ep;                                                                       \
		e.key = itf;                                                                        \
		e.data = (void *)md;                                                                \
		ep = hsearch(e, FIND);                                                              \
		if (ep) {                                                                           \
			ep->data = (void *)md;                                                      \
		} else {                                                                            \
			TRN_LOG_DEBUG(                                                              \
				"inserting [%s] for first time. allocate memory for interface key," \
				" since RPC XDR will eventually free its value.",                   \
				itf);                                                               \
			e.key = malloc(sizeof(char) * strlen(itf));                                 \
			strcpy(e.key, itf);                                                         \
			ep = hsearch(e, ENTER);                                                     \
		}                                                                                   \
		if (!ep)                                                                            \
			return -1;                                                                  \
		return 0;                                                                           \
	} while (0)

#define INTF_FIND()                                                            \
	do {                                                                   \
		ENTRY e, *ep;                                                  \
		e.key = itf;                                                   \
		ep = hsearch(e, FIND);                                         \
		if (!ep) {                                                     \
			return NULL;                                           \
		}                                                              \
		return ep->data;                                               \
	} while (0)

#define INTF_DELETE()                                                          \
	do {                                                                   \
		TRN_LOG_DEBUG("Delete: [%s]", itf);                            \
		ENTRY e, *ep;                                                  \
		e.key = itf;                                                   \
		ep = hsearch(e, FIND);                                         \
		if (ep) {                                                      \
			free(ep->key);                                         \
			free(ep->data);                                        \
			TRN_LOG_DEBUG("Deleted: [%s]", itf);                   \
		}                                                              \
	} while (0)

int trn_itf_table_init();
void trn_itf_table_free();
int trn_itf_table_insert(char *itf, struct user_metadata_t *md);
struct user_metadata_t *trn_itf_table_find(char *itf);
void trn_itf_table_delete(char *itf);
int trn_vif_table_insert(char *itf, struct agent_user_metadata_t *md);
struct agent_user_metadata_t *trn_vif_table_find(char *itf);
void trn_vif_table_delete(char *itf);
