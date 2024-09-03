# use the Node.js Docker image as builder
FROM node:alpine as builder

# create the directory inside the container
WORKDIR /app

# copy the package.json files from local machine to the workdir in container
COPY package*.json ./

# run npm install
RUN npm install

# copy the generated modules and all other files to the container
COPY . .

# run npm build
RUN npm run build

# create the nginx container
FROM nginx

# copy files from the builder to nginx
COPY --from=builder /app/dist /var/www/html

# copy the nginx config
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# nginx uses port 5000 so expose it
EXPOSE 5000

# start nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]