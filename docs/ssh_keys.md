# SSH Keys

SSH Keys in Exordos are used to manage SSH key pairs for secure access to nodes, node sets, and elements.

## Overview

SSH keys are managed through the `exordos secret ssh_keys` command group. The system supports:

- Adding SSH keys to nodes, node sets, elements, or all realm nodes
- Updating SSH key
- Deleting and clearing ssh keys

## Commands

### Add SSH Key

Add a new SSH key to the Exordos installation.

**Command:**

```bash
exordos secret ssh_keys add [OPTIONS]
```

**Examples:**

1. **Add SSH key to a specific node:**

```bash
exordos secret ssh_keys add \
  --node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 \
  --user ubuntu \
  --target_public_key ~/.ssh/id_rsa.pub
```

1. **Add SSH key to a node set:**

```bash
exordos secret ssh_keys add \
  --node_set 3dd80961-4ef8-5345-c0d2-1f31fe4783d8 \
  --user centos \
  --target_public_key /home/admin/.ssh/id_ed25519.pub
```

1. **Add SSH key to an element:**

```bash
exordos secret ssh_keys add \
  --element dbaas \
  --user postgres \
  --target_public_key ~/.ssh/id_rsa.pub
```

1. **Add SSH key to all realm nodes:**

```bash
exordos secret ssh_keys add \
  --realm \
  --user admin \
  --target_public_key ~/.ssh/id_ed25519.pub
```

1. **Add SSH key with custom metadata:**

```bash
exordos secret ssh_keys add \
  --node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 \
  --name production-ssh-key \
  --description "Production environment SSH key" \
  --user ubuntu \
  --target_public_key ~/.ssh/id_rsa.pub
```

**Short Form:**

```bash
exordos secret ssh_keys a --realm --target_public_key ~/.ssh/id_rsa.pub
```

### Update SSH Key

Update an existing SSH key's metadata.

**Command:**

```bash
exordos secret ssh_keys update [OPTIONS] <UUID>
```

**Examples:**

1. **Update SSH key name and description:**

```bash
exordos secret ssh_keys update \
  2cc70850-3df7-4234-b9c1-0e20ed3672c7 \
  --name production-ssh-key \
  --description "Updated production SSH key"
```

1. **Update SSH key project:**

```bash
exordos secret ssh_keys update \
  2cc70850-3df7-4234-b9c1-0e20ed3672c7 \
  --project-id 3dd80961-4ef8-5345-c0d2-1f31fe4783d8
```

**Short Form:**

```bash
exordos secret ssh_keys u 2cc70850-3df7-4234-b9c1-0e20ed3672c7 -n new-name -D "New description"
```

## Target Types

SSH keys can be deployed to different target types:

### Node Target

Deploy SSH key to a single node by specifying its UUID.

```bash
exordos secret ssh_keys add --node <NODE_UUID> --user <USERNAME> --target_public_key <KEY_PATH>
```

### Node Set Target

Deploy SSH key to all nodes in a set.

```bash
exordos secret ssh_keys add --node_set <SET_UUID> --user <USERNAME> --target_public_key <KEY_PATH>
```

### Element Target

Deploy SSH key to all nodes associated with an element.

```bash
exordos secret ssh_keys add --element <ELEMENT_NAME> --user <USERNAME> --target_public_key <KEY_PATH>
```

### Realm Target

Deploy SSH key to all nodes and sets in the realm.

```bash
exordos secret ssh_keys add --realm --user <USERNAME> --target_public_key <KEY_PATH>
```

## Common Workflows

### Workflow 1: Add SSH Key to Production Nodes

```bash
# 1. Add SSH key to production node set
exordos secret ssh_keys add \
  --node_set production-nodes \
  --target_public_key ~/.ssh/production_id_rsa.pub

# 2. Verify the key was created
exordos secret ssh_keys list
```

### Workflow 2: Deploy SSH Key to New Element

```bash
# 1. Create element
exordos e e install dbaas

# 2. Add SSH key to the element
exordos secret ssh_keys add \
  --element dbaas \
  --user postgres \
  --target_public_key ~/.ssh/dbaas_id_ed25519.pub
```

### Workflow 3: Bulk Deploy to Realm

```bash
# Deploy SSH key to all nodes in the realm
exordos secret ssh_keys add \
  --realm \
  --user admin \
  --target_public_key ~/.ssh/realm_admin.pub
```

### Workflow 4: Clear SSH Keys

```bash
# Clear all SSH keys
exordos secret ssh_keys clear -y
```
