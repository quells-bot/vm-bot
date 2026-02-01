# Environment Configuration

## System Information

- **Operating System**: Ubuntu 25.10 (aarch64/ARM64)
- **Kernel**: Linux 6.17.0-12-generic
- **Architecture**: ARM64
- **Platform**: linux
- **Working Directory**: `/home/sprite/claude`
- **User**: sprite

## Development Environment

### Go
- **Version**: go1.25.6 linux/arm64
- **Installed**: Yes
- **Command**: `go`

### Node.js
- **Version**: v24.13.0
- **npm Version**: 11.8.0
- **Installed via**: nvm (Node Version Manager)
- **Commands**: `node`, `npm`, `npx`

## Git Repository

- **Status**: Initialized
- **Current Branch**: main
- **Latest Commit**: d3ef4bf - initial commit

## Permissions & Access

This is a virtual machine with full access. Passwordless sudo is enabled.

Claude has free reign to:
- Install packages and dependencies
- Modify system configurations
- Create, read, update, and delete files
- Execute commands and scripts
- Set up development environments
- Run servers and services

## Common Tasks

### Package Management

**Ubuntu/Debian (apt)**:
```bash
sudo apt update
sudo apt install <package>
```

**Go modules**:
```bash
go mod init <module-name>
go get <package>
go mod tidy
```

**Node.js (npm)**:
```bash
npm install <package>
npm install -g <package>  # global install
```

**Node.js (via nvm)**:
```bash
nvm install <version>
nvm use <version>
nvm list
```

### Development Workflow

**Go**:
```bash
go run main.go           # Run
go build                 # Compile
go test                  # Test
go fmt                   # Format
```

**Node.js**:
```bash
npm init                 # Initialize project
npm start                # Start (if configured)
npm test                 # Test (if configured)
node index.js            # Run directly
```

## Notes

- This environment is specifically configured for development work
- Both Go and Node.js ecosystems are available for polyglot projects
- ARM64 architecture may require specific binary builds for some tools
- Git is configured and ready for version control operations
